"""Uploads one raw evidence file to the backend over HTTP (never over the WebSocket)."""

from datetime import datetime
from pathlib import Path

import httpx

from src.exceptions import UploadError
from src.security.auth import BearerAuth
from src.state.audit_logger import audit

_TIMEOUT_SECONDS = 60.0


class EvidenceUploader:
    def __init__(
        self, base_url: str, token: str, *, transport: httpx.BaseTransport | None = None
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url, auth=BearerAuth(token), timeout=_TIMEOUT_SECONDS, transport=transport
        )

    def close(self) -> None:
        self._client.close()

    def upload(
        self,
        path: Path,
        *,
        session_id: str,
        operation_id: str,
        sequence: int,
        part: int,
        sha256_agent: str,
        size_bytes: int,
        acquired_at: datetime,
        raw_source: str,
        tool_version: str | None,
        android_version: str | None,
        device_build: str | None,
        privilege_state: str | None,
    ) -> None:
        """POST the file bytes as they are on disk. Raises `UploadError` unless the backend
        answers 201 (a SHA-256 mismatch is 422 and is reported, not retried)."""
        fields = {
            "session_id": session_id,
            "operation_id": operation_id,
            "sequence": str(sequence),
            "part": str(part),
            "sha256_agent": sha256_agent,
            "size_bytes": str(size_bytes),
            "acquired_at": acquired_at.isoformat(),
            "raw_source": raw_source,
        }
        optional = {
            "tool_version": tool_version,
            "android_version": android_version,
            "device_build": device_build,
            "privilege_state": privilege_state,
        }
        fields.update({key: value for key, value in optional.items() if value is not None})
        try:
            with path.open("rb") as handle:
                response = self._client.post(
                    "/api/evidence/upload",
                    data=fields,
                    files={"file": (path.name, handle, "application/octet-stream")},
                )
        except (httpx.HTTPError, OSError) as exc:
            audit("upload_failed", type(exc).__name__, session_id=session_id, sequence=sequence)
            raise UploadError(f"upload failed: {type(exc).__name__}") from exc
        if response.status_code != 201:
            audit(
                "upload_rejected",
                f"HTTP {response.status_code}",
                session_id=session_id,
                sequence=sequence,
            )
            raise UploadError(f"backend rejected the upload (HTTP {response.status_code})")
        audit("upload_done", session_id=session_id, sequence=sequence, part=part)
