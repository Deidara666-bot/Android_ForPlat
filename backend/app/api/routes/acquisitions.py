import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.agent import Agent
from app.models.case import Case
from app.models.device import Device
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
    body: AcquisitionCreate, db: Annotated[Session, Depends(get_db)]
) -> AcquisitionDetailOut:
    service = AcquisitionService(db)
    try:
        operations = service.operations_for(body.profile, body.operation)
    except OperationNotMappedError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "jenis": "OperationNotMappedError",
                "pesan": f"operasi '{body.operation}' belum dipetakan",
            },
        ) from None
    except OperationNotAllowedError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "jenis": "OperationNotAllowedError",
                "pesan": f"operasi '{body.operation}' bukan operasi allowlist",
            },
        ) from None
    except UnknownProfileError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"jenis": "UnknownProfileError", "pesan": f"profil '{body.profile}' tidak ada"},
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

    session, _ = service.create_session(body.case_id, device, agent, operations, body.profile)
    for operation in operations:
        if not await manager.send(agent.agent_id, service.build_job(session, operation, {})):
            service.mark_failed(session, "agent disconnected before the job was delivered")
            raise HTTPException(status.HTTP_409_CONFLICT, detail="agent disconnected")
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
