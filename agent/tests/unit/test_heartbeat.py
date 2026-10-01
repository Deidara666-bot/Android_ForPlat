import asyncio
import json

import pytest

from src.models import AgentState
from src.transport.heartbeat import heartbeat_message, send_heartbeats


class _FakeSocket:
    def __init__(self) -> None:
        self.sent: list[str] = []

    async def send(self, message: str) -> None:
        self.sent.append(message)


def test_heartbeat_payload_shape() -> None:
    payload = json.loads(heartbeat_message(AgentState.connected, 2))
    assert payload == {"type": "heartbeat", "state": "connected", "device_count": 2}


@pytest.mark.asyncio
async def test_heartbeats_are_sent_repeatedly_until_cancelled() -> None:
    socket = _FakeSocket()
    task = asyncio.create_task(send_heartbeats(socket, 0.01))
    await asyncio.sleep(0.1)
    task.cancel()
    await asyncio.gather(task, return_exceptions=True)
    assert len(socket.sent) >= 3
    assert all(json.loads(message)["type"] == "heartbeat" for message in socket.sent)
