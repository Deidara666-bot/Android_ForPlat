import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.constants import PACKAGE_NAME_PATTERN
from app.research.coverage import CoverageService
from app.schemas.coverage import CoverageRowOut
from app.services.case_service import CaseService

router = APIRouter(prefix="/cases", tags=["coverage"], dependencies=[Depends(get_current_user)])


@router.get(
    "/{case_id}/coverage",
    response_model=list[CoverageRowOut],
    summary="Source coverage per subject and part (why a fact can or cannot be FALSE)",
)
def get_coverage(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    subject: Annotated[str | None, Query(pattern=PACKAGE_NAME_PATTERN)] = None,
) -> list[CoverageRowOut]:
    if CaseService(db).get(case_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="case tidak ditemukan")
    return [
        CoverageRowOut(
            subject=row.subject,
            scope=row.scope.value,
            operation_id=row.coverage.operation_id,
            raw_source=row.coverage.raw_source,
            session_id=row.coverage.session_id,
            availability_status=row.coverage.availability_status,
            parse_complete=row.coverage.parse_complete,
            can_be_false=row.coverage.can_be_false,
            evidence_ids=row.coverage.evidence_ids,
            reason=row.coverage.reason,
        )
        for row in CoverageService.matrix(db, case_id, subject)
    ]
