import logging
import uuid
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import decode_access_token
from app.services.auth_service import AuthService
from app.ws.manager import dashboard_manager

log = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/dashboard")
async def dashboard_ws(
    websocket: WebSocket,
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str | None, Query()] = None,
) -> None:
    """Live change notifications for an examiner's dashboard (JWT in the query string)."""
    user = None
    if token:
        try:
            user_id = uuid.UUID(str(decode_access_token(token)["sub"]))
            user = AuthService(db).get_by_id(user_id)
        except (jwt.InvalidTokenError, KeyError, ValueError):
            user = None
    if user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    dashboard_manager.register(websocket)
    try:
        while True:
            await websocket.receive_text()  # the dashboard only listens; ignore anything it sends
    except WebSocketDisconnect:
        pass
    finally:
        dashboard_manager.disconnect(websocket)
