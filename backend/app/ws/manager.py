from typing import Any

from fastapi import WebSocket


class WebSocketConnectionManager:
    """Keeps one live WebSocket per agent_id; a newer connection replaces the older one."""

    def __init__(self) -> None:
        self._connections: dict[str, WebSocket] = {}

    def register(self, agent_id: str, websocket: WebSocket) -> None:
        self._connections[agent_id] = websocket

    def disconnect(self, agent_id: str, websocket: WebSocket) -> None:
        # Only drop the entry if it is still this connection (a reconnect may have replaced it).
        if self._connections.get(agent_id) is websocket:
            del self._connections[agent_id]

    def connected_agent_ids(self) -> list[str]:
        return sorted(self._connections)

    async def send(self, agent_id: str, message: dict[str, Any]) -> bool:
        websocket = self._connections.get(agent_id)
        if websocket is None:
            return False
        await websocket.send_json(message)
        return True

    async def broadcast(self, message: dict[str, Any]) -> None:
        for agent_id in self.connected_agent_ids():
            await self.send(agent_id, message)


class DashboardConnectionManager:
    """Examiner dashboards listening for live changes. Messages are small JSON notifications."""

    def __init__(self) -> None:
        self._sockets: set[WebSocket] = set()

    def register(self, websocket: WebSocket) -> None:
        self._sockets.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._sockets.discard(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        for websocket in list(self._sockets):
            try:
                await websocket.send_json(message)
            except Exception:  # noqa: BLE001 - a dead dashboard must not break the broadcaster
                self._sockets.discard(websocket)


manager = WebSocketConnectionManager()
dashboard_manager = DashboardConnectionManager()
