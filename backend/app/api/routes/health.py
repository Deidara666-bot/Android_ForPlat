from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.constants import APP_VERSION
from app.schemas.rules import RulesHealth

router = APIRouter(tags=["health"])


class HealthOut(BaseModel):
    status: str
    app_env: str
    database: str
    alembic_revision: str | None
    app_version: str
    rules: RulesHealth | None  # None: the startup load was not attempted (tests only)


class HealthUnavailableOut(BaseModel):
    status: str
    database: str


@router.get(
    "/health",
    response_model=HealthOut,
    responses={503: {"model": HealthUnavailableOut, "description": "Database unreachable"}},
    summary="Service health, including a real database round-trip",
)
def health(request: Request, db: Annotated[Session, Depends(get_db)]) -> HealthOut | JSONResponse:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            status_code=503, content={"status": "unavailable", "database": "unreachable"}
        )
    try:
        revision = db.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
    except SQLAlchemyError:
        db.rollback()
        revision = None  # database answers, but has not been migrated
    return HealthOut(
        status="ok",
        app_env=get_settings().app_env,
        database="reachable",
        alembic_revision=revision,
        app_version=APP_VERSION,
        rules=getattr(request.app.state, "rules_status", None),
    )
