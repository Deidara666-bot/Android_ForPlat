import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.constants import ActorType, AuditEventType
from app.models.audit_log import AuditLog


class AuditService:
    """Writes audit rows. Each record is committed on its own so that a request which is then
    rejected (HTTP error) still leaves its trace."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def record(
        self,
        event_type: AuditEventType,
        actor_type: ActorType,
        *,
        actor_id: uuid.UUID | None = None,
        object_type: str | None = None,
        object_id: uuid.UUID | None = None,
        reason: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> AuditLog:
        row = AuditLog(
            actor_type=actor_type.value,
            actor_id=actor_id,
            event_type=event_type.value,
            object_type=object_type,
            object_id=object_id,
            reason=reason,
            details=details or {},
        )
        self._db.add(row)
        self._db.commit()
        return row
