from typing import Any

import httpx
from tenacity import (
    RetryCallState,
    Retrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from tenacity.wait import wait_base

from src.exceptions import AgentError
from src.security.auth import BearerAuth
from src.state.audit_logger import audit

MAX_ATTEMPTS = 5


class _Retryable(Exception):
    """Transient failure (network error or HTTP 5xx) worth another attempt."""


class ApiClient:
    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        wait: wait_base | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url, auth=BearerAuth(token), timeout=5.0, transport=transport
        )
        self._wait = wait or wait_exponential(multiplier=0.5, min=0.5, max=8)

    def close(self) -> None:
        self._client.close()

    def get_json(self, path: str) -> dict[str, Any]:
        retrying = Retrying(
            stop=stop_after_attempt(MAX_ATTEMPTS),
            wait=self._wait,
            retry=retry_if_exception_type(_Retryable),
            before_sleep=lambda state: self._audit_failure(path, state),
            reraise=True,
        )
        try:
            return retrying(self._get_once, path)
        except _Retryable as exc:
            audit("api_request_gave_up", str(exc), path=path, attempts=MAX_ATTEMPTS)
            raise AgentError(f"backend unreachable after {MAX_ATTEMPTS} attempts: {exc}") from exc

    def _get_once(self, path: str) -> dict[str, Any]:
        try:
            response = self._client.get(path)
        except httpx.TransportError as exc:
            raise _Retryable(type(exc).__name__) from exc
        if response.status_code >= 500:
            raise _Retryable(f"HTTP {response.status_code}")
        if response.status_code in (401, 403):
            audit("api_request_rejected", f"HTTP {response.status_code}", path=path)
            raise AgentError(f"backend rejected the agent token (HTTP {response.status_code})")
        if response.status_code >= 400:
            raise AgentError(f"backend returned HTTP {response.status_code} for {path}")
        body: dict[str, Any] = response.json()
        return body

    @staticmethod
    def _audit_failure(path: str, state: RetryCallState) -> None:
        outcome = state.outcome
        reason = str(outcome.exception()) if outcome is not None else None
        audit("api_request_failed", reason, path=path, attempt=state.attempt_number)
