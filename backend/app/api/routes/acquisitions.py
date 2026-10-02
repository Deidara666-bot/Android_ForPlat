import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.constants import ActorType, AuditEventType
from app.models.agent import Agent
from app.models.case import Case
from app.models.device import Device
from app.models.user import User
from app.schemas.acquisition import (
    AcquisitionCreate,
    AcquisitionDetailOut,
    AcquisitionOperationOut,
    AcquisitionSessionOut,
)
from app.services.acquisition_service import (
    AcquisitionService,
    OperationNotAllowedError,
    OperationNotMappedError,
    UnknownProfileError,
)
from app.services.audit_service import AuditService
from app.ws.manager import manager

router = APIRouter(
    prefix="/acquisitions", tags=["acquisitions"], dependencies=[Depends(get_current_user)]
)


def _detail(session: object, service: AcquisitionService) -> AcquisitionDetailOut:
    base = AcquisitionSessionOut.model_validate(session, from_attributes=True)
    operations = [
        AcquisitionOperationOut.model_validate(item, from_attributes=True)
        for item in service.list_operations(base.id)
    ]
    return AcquisitionDetailOut(**base.model_dump(), operations=operations)


@router.post(
    "",
    response_model=AcquisitionDetailOut,
    status_code=status.HTTP_201_CREATED,
    summary="Start an acquisition session",
)
async def create_acquisition(
    body: AcquisitionCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> AcquisitionDetailOut:
    service = AcquisitionService(db)
    audit = AuditService(db)
    try:
        operations = service.operations_for(body.profile, body.operation)
    except (OperationNotMappedError, OperationNotAllowedError, UnknownProfileError) as exc:
        kind = type(exc).__name__
        requested = body.operation if body.operation is not None else body.profile
        audit.record(
            AuditEventType.operation_rejected,
            ActorType.user,
            actor_id=user.id,
            object_type="case",
            object_id=body.case_id,
            reason=kind,
            details={"requested": (requested or "")[:64]},
        )
        messages = {
            "OperationNotMappedError": f"operasi '{body.operation}' belum dipetakan",
            "OperationNotAllowedError": f"operasi '{body.operation}' bukan operasi allowlist",
            "UnknownProfileError": f"profil '{body.profile}' tidak ada",
        }
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, detail={"jenis": kind, "pesan": messages[kind]}
        ) from None

    if db.get(Case, body.case_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="case not found")
    device = db.get(Device, body.device_id)
    if device is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="device not found")

    agent = db.get(Agent, device.last_agent_id) if device.last_agent_id is not None else None
    if agent is None or agent.agent_id not in manager.connected_agent_ids():
        raise HTTPException(
            status.HTTP_409_CONFLICT, detail="agent for this device is not connected"
        )

    session, rows = service.create_session(body.case_id, device, agent, operations, body.profile)
    for row in rows:
        job = service.build_job(session, row, device.serial, {})
        if not await manager.send(agent.agent_id, job):
            service.mark_failed(session, "agent disconnected before the job was delivered")
            raise HTTPException(status.HTTP_409_CONFLICT, detail="agent disconnected")
        audit.record(
            AuditEventType.job_issued,
            ActorType.user,
            actor_id=user.id,
            object_type="acquisition_session",
            object_id=session.id,
            details={"operation": row.operation_id, "sequence": row.sequence},
        )
    return _detail(session, service)


@router.get("/{session_id}", response_model=AcquisitionDetailOut, summary="Read a session")
def read_acquisition(
    session_id: uuid.UUID, db: Annotated[Session, Depends(get_db)]
) -> AcquisitionDetailOut:
    service = AcquisitionService(db)
    session = service.get_session(session_id)
    if session is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="acquisition session not found")
    return _detail(session, service)
