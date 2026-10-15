"""Start an analysis and read it back (REF §API2, §ENGINE).

`POST .../analyze` runs the rule engine for the purpose asked and answers with the run id. The
three `GET` routes only read: `evaluations` returns every family, profile and condition of the
run (skipped, insufficient and conflicting ones included), `findings` only the matched profiles.
Nothing here changes an evaluation or a finding.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.build_info import UNKNOWN_COMMIT
from app.research.engine.windows import InvalidWindowError, make_window
from app.research.rule_engine import CodeCommitUnverifiedError, NoSubjectsError
from app.research.rules.errors import RuleLoadError
from app.schemas.evaluation import (
    AnalyzeIn,
    AnalyzeOut,
    EvaluationsOut,
    FindingsOut,
    RunOut,
)
from app.services.case_service import CaseService
from app.services.correlation_service import CaseNotFoundError, CorrelationService
from app.services.evaluation_query_service import EvaluationQueryService

router = APIRouter(tags=["analysis"], dependencies=[Depends(get_current_user)])

_CASE_NOT_FOUND = "case tidak ditemukan"
_RUN_NOT_FOUND = "run tidak ditemukan"


@router.post(
    "/cases/{case_id}/analyze",
    response_model=AnalyzeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Evaluate the rules for a case and record the whole run",
)
def analyze(
    case_id: uuid.UUID,
    body: AnalyzeIn,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> AnalyzeOut:
    try:
        window = make_window(body.window_start, body.window_end)
    except InvalidWindowError as error:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"code": InvalidWindowError.code, "message": str(error)},
        ) from error
    code_commit = getattr(request.app.state, "code_commit", UNKNOWN_COMMIT)
    try:
        run_id = CorrelationService(db, code_commit).analyze(
            case_id, body.evidence_mode, body.run_purpose, window, body.subjects
        )
    except CaseNotFoundError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_CASE_NOT_FOUND) from error
    except NoSubjectsError as error:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"code": NoSubjectsError.code, "message": str(error)},
        ) from error
    except RuleLoadError as error:
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail={"code": error.code.value, "path": error.path}
        ) from error
    except CodeCommitUnverifiedError as error:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail={"code": CodeCommitUnverifiedError.code, "message": str(error)},
        ) from error
    return AnalyzeOut(correlation_run_id=run_id)


@router.get(
    "/correlation-runs/{run_id}",
    response_model=RunOut,
    summary="One analysis run: purpose, window, subjects and the hashes that identify it",
)
def get_run(run_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]) -> RunOut:
    run = EvaluationQueryService(db).get_run(run_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_RUN_NOT_FOUND)
    return EvaluationQueryService.run_out(run)


def _resolve_run(
    service: EvaluationQueryService, db: Session, case_id: uuid.UUID, run_id: uuid.UUID | None
) -> RunOut | None:
    """The run asked for (of this case), else the latest run of the case, else None."""
    if CaseService(db).get(case_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_CASE_NOT_FOUND)
    run = service.get_run(run_id) if run_id is not None else service.latest_run(case_id)
    if run is None:
        if run_id is not None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_RUN_NOT_FOUND)
        return None
    if run.case_id != case_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=_RUN_NOT_FOUND)
    return service.run_out(run)


@router.get(
    "/cases/{case_id}/evaluations",
    response_model=EvaluationsOut,
    summary="Every family, profile and condition of a run, with reasons and supporting facts",
)
def list_evaluations(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    run: Annotated[uuid.UUID | None, Query()] = None,
) -> EvaluationsOut:
    service = EvaluationQueryService(db)
    resolved = _resolve_run(service, db, case_id, run)
    if resolved is None:
        return EvaluationsOut(run=None, families=[])
    row = service.get_run(resolved.id)
    assert row is not None
    return EvaluationsOut(run=resolved, families=service.evaluations(row))


@router.get(
    "/cases/{case_id}/findings",
    response_model=FindingsOut,
    summary="Findings of a run: only the matched profiles, with their limitations",
)
def list_findings(
    case_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
    run: Annotated[uuid.UUID | None, Query()] = None,
) -> FindingsOut:
    service = EvaluationQueryService(db)
    resolved = _resolve_run(service, db, case_id, run)
    if resolved is None:
        return FindingsOut(run=None, findings=[])
    row = service.get_run(resolved.id)
    assert row is not None
    return FindingsOut(run=resolved, findings=service.findings(row))
