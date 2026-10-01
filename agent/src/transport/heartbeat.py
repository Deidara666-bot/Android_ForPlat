import asyncio
import json
from collections.abc import Callable
from typing import Protocol

from src.models import AgentState


class _Sender(Protocol):
    async def send(self, message: str) -> None: ...


def heartbeat_message(state: AgentState, device_count: int) -> str:
    return json.dumps({"type": "heartbeat", "state": state.value, "device_count": device_count})


async def send_heartbeats(
    websocket: _Sender,
    interval_seconds: float,
    device_count: Callable[[], int] = lambda: 0,
    state: Callable[[], AgentState] = lambda: AgentState.connected,
) -> None:
    """Send a heartbeat every `interval_seconds` until cancelled or the socket fails."""
    while True:
        await websocket.send(heartbeat_message(state(), device_count()))
        await asyncio.sleep(interval_seconds)
