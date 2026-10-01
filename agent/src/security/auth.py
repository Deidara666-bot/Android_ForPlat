from collections.abc import Generator

import httpx


class BearerAuth(httpx.Auth):
    """Adds `Authorization: Bearer <AGENT_TOKEN>`; the token never appears in repr or logs."""

    def __init__(self, token: str) -> None:
        self._token = token

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response]:
        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request

    def __repr__(self) -> str:
        return "BearerAuth(token=***)"
