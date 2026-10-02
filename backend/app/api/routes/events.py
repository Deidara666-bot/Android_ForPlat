import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.events import ArtifactOut, EventOut
from app.services.event_query_service import EventQueryService, UnknownEventTypeError

router = APIRouter(prefix="/cases", tags=["events"], dependencies=[Depends(get_current_user)])

_CASE_NOT_FOUND = "case tidak ditemukan"


def _require_case(service: EventQueryService, case_id: uuid.UUID) -> None:
    if service.get_case(case_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_CASE_NOT_FOUND)


@router.get(
    "/{case_id}/artifacts",
    response_model=list[ArtifactOut],
    summary="Artifacts of a case (failed and empty included) with provenance",
)
def list_artifacts(
    case_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]
) -> list[ArtifactOut]:
    service = EventQueryService(db)
    _require_case(service, case_id)
    return service.artifacts(case_id)


@router.get(
    "/{case_id}/events",
    response_model=list[EventOut],
    summary="Normalized facts of a case with provenance to the raw evidence",
)
def list_events(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    event_type: str | None = None,
) -> list[EventOut]:
    service = EventQueryService(db)
    _require_case(service, case_id)
    try:
        return service.events(case_id, event_type)
    except UnknownEventTypeError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"event_type tidak ada dalam katalog: {event_type}",
        ) from None
