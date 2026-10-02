import asyncio
import json
import logging

from tenacity import AsyncRetrying, RetryCallState, retry_if_exception_type, stop_after_attempt
from tenacity.wait import wait_base, wait_exponential
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed, InvalidHandshake, InvalidStatus

from src.acquisition.acquisition_runner import AcquisitionRunner
from src.config import Settings
from src.device.device_detection import DeviceMonitor
from src.exceptions import AgentError
from src.models import AgentState
from src.state.audit_logger import audit
from src.state.state_machine import AgentStateMachine
from src.transport.heartbeat import send_heartbeats
from src.transport.uploader import EvidenceUploader

log = logging.getLogger("agent.ws")

# ~70 s of backoff in total: long enough to ride out a backend restart, bounded so the agent
# eventually gives up with a clear error instead of retrying forever.
MAX_CONNECT_ATTEMPTS = 12


async def _connect_once(url: str, token: str) -> ClientConnection:
    try:
        return await connect(
            url, additional_headers={"Authorization": f"Bearer {token}"}, proxy=None
        )
    except InvalidStatus as exc:
        audit("ws_rejected", f"HTTP {exc.response.status_code}")
        raise AgentError(
            f"backend rejected the WebSocket (HTTP {exc.response.status_code})"
        ) from exc


def _audit_failure(state: RetryCallState) -> None:
    outcome = state.outcome
    reason = type(outcome.exception()).__name__ if outcome is not None else None
    audit("ws_connect_failed", reason, attempt=state.attempt_number)


async def connect_with_retry(
    url: str, token: str, *, wait: wait_base | None = None
) -> ClientConnection:
    retrying = AsyncRetrying(
        stop=stop_after_attempt(MAX_CONNECT_ATTEMPTS),
        wait=wait or wait_exponential(multiplier=0.5, min=0.5, max=8),
        retry=retry_if_exception_type((OSError, TimeoutError, InvalidHandshake)),
        before_sleep=_audit_failure,
        reraise=True,
    )
    try:
        return await retrying(_connect_once, url, token)
    except (OSError, TimeoutError, InvalidHandshake) as exc:
        audit("ws_gave_up", type(exc).__name__, attempts=MAX_CONNECT_ATTEMPTS)
        raise AgentError(
            f"backend WebSocket unreachable after {MAX_CONNECT_ATTEMPTS} attempts"
        ) from exc


async def _handle_messages(websocket: ClientConnection, runner: AcquisitionRunner) -> None:
    """Server -> agent messages. Only `job` is acted on; each is run to completion in order."""
    async for raw in websocket:
        try:
            message = json.loads(raw)
        except (TypeError, ValueError):
            continue
        if not isinstance(message, dict) or message.get("type") != "job":
            continue
        status = await runner.handle_job(message)
        if status is not None:
            await websocket.send(json.dumps(status))


async def run_forever(
    settings: Settings, machine: AgentStateMachine, *, wait: wait_base | None = None
) -> None:
    """Connect, heartbeat until the socket drops, then reconnect. Ends only on AgentError/cancel."""
    reconnect = False
    monitor = DeviceMonitor(adb_path=settings.adb_path)
    runner = AcquisitionRunner(
        EvidenceUploader(settings.backend_base_url, settings.agent_token),
        adb_path=settings.adb_path,
    )
    while True:
        websocket = await connect_with_retry(
            settings.backend_ws_url, settings.agent_token, wait=wait
        )
        machine.transition_to(AgentState.connected)
        audit("ws_reconnected" if reconnect else "ws_connected", agent_id=settings.agent_id)
        log.info("websocket %s", "reconnected" if reconnect else "connected")
        monitor.reset_reporting()  # a fresh connection must be told the full device list
        interval = settings.poll_interval_seconds
        tasks = {
            asyncio.create_task(
                send_heartbeats(
                    websocket, interval, lambda: monitor.connected_count, lambda: machine.state
                )
            ),
            asyncio.create_task(monitor.run(websocket, interval)),
            asyncio.create_task(_handle_messages(websocket, runner)),
        }
        try:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        finally:
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            await websocket.close()
        machine.transition_to(AgentState.disconnected)
        audit("ws_disconnected", agent_id=settings.agent_id)
        log.warning("websocket closed; reconnecting")
        reconnect = True


__all__ = ["ConnectionClosed", "connect_with_retry", "run_forever"]
