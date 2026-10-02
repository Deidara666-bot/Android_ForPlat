import logging
from typing import Annotated

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.agent import Agent
from app.schemas.acquisition import JobStatusIn
from app.schemas.device import DeviceReportItem
from app.services.acquisition_service import AcquisitionService
from app.services.agent_service import AgentService
from app.services.device_service import DeviceService
from app.ws.manager import dashboard_manager, manager

log = logging.getLogger(__name__)
router = APIRouter()


def _bearer_token(websocket: WebSocket) -> str | None:
    scheme, _, value = websocket.headers.get("authorization", "").partition(" ")
    return value.strip() or None if scheme.lower() == "bearer" else None


@router.websocket("/ws/agent")
async def agent_ws(websocket: WebSocket, db: Annotated[Session, Depends(get_db)]) -> None:
    """Heartbeat/status channel. Evidence bytes never travel here (HTTP upload only)."""
    service = AgentService(db)
    token = _bearer_token(websocket)
    agent: Agent | None = service.find_by_token(token) if token else None
    if agent is None:
        # Authenticate before accept: the handshake is rejected.
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    agent_id = agent.agent_id
    manager.register(agent_id, websocket)
    service.touch(agent)
    log.info("agent connected: %s", agent_id)
    await dashboard_manager.broadcast(
        {"type": "agent_status", "agent_id": agent_id, "connected": True}
    )
    try:
        while True:
            message = await websocket.receive_json()
            if not isinstance(message, dict):
                continue
            if message.get("type") == "heartbeat":
                service.touch(agent)
            elif message.get("type") == "device_report":
                try:
                    items = [DeviceReportItem(**raw) for raw in message.get("devices", [])]
                except (ValidationError, TypeError):
                    log.warning("invalid device_report from %s ignored", agent_id)
                    continue
                DeviceService(db).apply_report(agent, items)
                await dashboard_manager.broadcast({"type": "devices_changed"})
            elif message.get("type") == "job_status":
                try:
                    status_in = JobStatusIn(**{k: v for k, v in message.items() if k != "type"})
                except (ValidationError, TypeError):
                    log.warning("invalid job_status from %s ignored", agent_id)
                    continue
                AcquisitionService(db).apply_job_status(agent, status_in)
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(agent_id, websocket)
        log.info("agent disconnected: %s", agent_id)
        await dashboard_manager.broadcast(
            {"type": "agent_status", "agent_id": agent_id, "connected": False}
        )
