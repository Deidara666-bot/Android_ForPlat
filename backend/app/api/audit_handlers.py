"""Audit trail for requests FastAPI rejects before the route code runs.

Two cases only: a failed authentication (401) and a request whose shape fails validation
(422), both limited to the routes that already write audit rows. The response sent to the
client is unchanged: after recording, the framework's default handler answers.

What is stored: method, path, HTTP status and (for 422) the names of the offending fields.
Never a token, a header, a field value or a validation message (which can echo the value).
"""

import logging
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Request
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.deps import get_db
from app.core.constants import ActorType, AuditEventType
from app.models.audit_log import AuditLog
from app.services.audit_service import AuditService

log = logging.getLogger(__name__)

AUDITED_PREFIXES = ("/api/acquisitions", "/api/evidence")
# The same (event, path) is written at most once per window: unauthenticated callers must
# not be able to grow the audit table without bound.
THROTTLE_WINDOW = timedelta(seconds=60)
_MAX_PATH_CHARS = 200
_MAX_FIELDS = 20


def _is_audited(request: Request) -> bool:
    return request.url.path.startswith(AUDITED_PREFIXES)


def _open_db(request: Request) -> tuple[Session, Generator[Session] | None]:
    """A session from the same provider the routes use (so tests' override applies)."""
    provider = request.app.dependency_overrides.get(get_db, get_db)
    produced: Any = provider()
    if isinstance(produced, Session):
        return produced, None
    return next(produced), produced


def _record(request: Request, event: AuditEventType, reason: str, extra: dict[str, Any]) -> None:
    path = request.url.path[:_MAX_PATH_CHARS]
    try:
        db, generator = _open_db(request)
        try:
            recent = db.scalar(
                select(AuditLog.id)
                .where(
                    AuditLog.event_type == event.value,
                    AuditLog.details["path"].astext == path,
                    AuditLog.occurred_at > datetime.now(UTC) - THROTTLE_WINDOW,
                )
                .limit(1)
            )
            if recent is None:
                AuditService(db).record(
                    event,
                    ActorType.system,  # the caller is unidentified or unauthenticated
                    reason=reason,
                    details={"method": request.method, "path": path, **extra},
                )
        finally:
            if generator is not None:
                generator.close()
    except SQLAlchemyError:
        # Auditing must never turn a 401/422 into a 500.
        log.warning("could not write the audit row for a rejected request", exc_info=True)


async def audit_http_exception(request: Request, exc: StarletteHTTPException) -> Response:
    if exc.status_code == 401 and _is_audited(request):
        _record(
            request,
            AuditEventType.authentication_failed,
            "invalid or missing credentials",
            {"http_status": 401},
        )
    return await http_exception_handler(request, exc)


async def audit_validation_error(request: Request, exc: RequestValidationError) -> Response:
    if _is_audited(request):
        names = {".".join(str(part) for part in err["loc"])[:100] for err in exc.errors()}
        fields = sorted(names)[:_MAX_FIELDS]
        _record(
            request,
            AuditEventType.request_validation_failed,
            "request validation failed",
            {"http_status": 422, "fields": fields},
        )
    return await request_validation_exception_handler(request, exc)
