import asyncio
import logging

from tenacity import AsyncRetrying, RetryCallState, retry_if_exception_type, stop_after_attempt
from tenacity.wait import wait_base, wait_exponential
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import ConnectionClosed, InvalidHandshake, InvalidStatus

from src.config import Settings
from src.exceptions import AgentError
from src.state.audit_logger import audit
from src.transport.heartbeat import send_heartbeats

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


async def _drain(websocket: ClientConnection) -> None:
    async for _ in websocket:  # server -> agent messages (jobs) are handled from v0.30
        pass


async def run_forever(settings: Settings, *, wait: wait_base | None = None) -> None:
    """Connect, heartbeat until the socket drops, then reconnect. Ends only on AgentError/cancel."""
    reconnect = False
    while True:
        websocket = await connect_with_retry(
            settings.backend_ws_url, settings.agent_token, wait=wait
        )
        audit("ws_reconnected" if reconnect else "ws_connected", agent_id=settings.agent_id)
        log.info("websocket %s", "reconnected" if reconnect else "connected")
        heartbeat = asyncio.create_task(send_heartbeats(websocket, settings.poll_interval_seconds))
        drain = asyncio.create_task(_drain(websocket))
        try:
            await asyncio.wait({heartbeat, drain}, return_when=asyncio.FIRST_COMPLETED)
        finally:
            for task in (heartbeat, drain):
                task.cancel()
            await asyncio.gather(heartbeat, drain, return_exceptions=True)
            await websocket.close()
        audit("ws_disconnected", agent_id=settings.agent_id)
        log.warning("websocket closed; reconnecting")
        reconnect = True


__all__ = ["ConnectionClosed", "connect_with_retry", "run_forever"]
