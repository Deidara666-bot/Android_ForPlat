"""Runs one backend job: resolve the operation ID, run adb, write raw bytes, hash, report."""

import asyncio
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.acquisition.command_allowlist import resolve_operation
from src.acquisition.evidence_writer import write_evidence
from src.device.adb_commands import RAW_SOURCE_LABEL
from src.device.adb_controller import adb_version, run_adb
from src.device.device_detection import collect_safe_metadata, detect_devices
from src.exceptions import AgentError, UploadError
from src.integrity.hashing import sha256_file
from src.models import AcquisitionJob
from src.state.audit_logger import audit
from src.transport.uploader import EvidenceUploader

RAW_ROOT = Path(__file__).resolve().parents[2] / "var" / "raw"
# v0.30 operations run one command each; multi-command operations arrive in v0.45.
_PART = 1
_PARTS_TOTAL = 1


class AcquisitionRunner:
    """Executes jobs one at a time. Evidence goes to disk byte-exact before it is hashed.

    The job names its device (`serial`) and its position (`sequence`); the agent chooses neither.
    """

    def __init__(
        self,
        uploader: EvidenceUploader,
        adb_path: str | None = None,
        raw_root: Path | None = None,
    ) -> None:
        self._uploader = uploader
        self._adb_path = adb_path
        self._raw_root = raw_root or RAW_ROOT
        self._tool_version: str | None = None
        self._device_context: dict[str, dict[str, Any]] = {}

    async def handle_job(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Return the `job_status` message, or None when the job is too malformed to report."""
        return await asyncio.to_thread(self.run_job, message)

    def run_job(self, message: dict[str, Any]) -> dict[str, Any] | None:
        try:
            job = AcquisitionJob(**message)
            uuid.UUID(job.session_id)  # the folder name comes from this value
        except (ValidationError, ValueError, TypeError) as exc:
            audit("job_rejected", "invalid job message", error_class=type(exc).__name__)
            return self._failed_from_raw(message, type(exc).__name__)

        digest: str | None = None
        size: int | None = None
        try:
            args = resolve_operation(job.operation, job.parameters)
            self._require_ready(job.serial)
            result = run_adb(args, job.serial, adb_path=self._adb_path)
            acquired_at = datetime.now(UTC)
            path = self._raw_root / job.session_id / f"{job.sequence}-{job.operation}-{_PART}.bin"
            size = write_evidence(path, result.stdout)
            digest = sha256_file(path)
            if result.returncode == 0:  # a failed command is never uploaded as acquired evidence
                context = self._context_for(job.serial)
                self._uploader.upload(
                    path,
                    session_id=job.session_id,
                    operation_id=job.operation,
                    sequence=job.sequence,
                    part=_PART,
                    sha256_agent=digest,
                    size_bytes=size,
                    acquired_at=acquired_at,
                    raw_source=RAW_SOURCE_LABEL[job.operation],
                    tool_version=self._tool_version,
                    android_version=context.get("android_version"),
                    device_build=context.get("device_build"),
                    privilege_state=context.get("privilege_state"),
                )
        except (AgentError, ValueError, OSError, KeyError) as exc:
            audit(
                "job_failed",
                type(exc).__name__,
                session_id=job.session_id,
                sequence=job.sequence,
                operation=job.operation,
                uploaded=not isinstance(exc, UploadError) and digest is not None,
            )
            # Keep the digest and size when the file exists locally but the upload failed.
            return self._status(
                job.session_id,
                job.sequence,
                job.operation,
                job.serial,
                sha256_agent=digest,
                size_bytes=size,
                error=type(exc).__name__,
            )

        audit(
            "job_done",
            session_id=job.session_id,
            sequence=job.sequence,
            operation=job.operation,
            returncode=result.returncode,
            size_bytes=size,
        )
        return self._status(
            job.session_id,
            job.sequence,
            job.operation,
            job.serial,
            sha256_agent=digest,
            size_bytes=size,
            returncode=result.returncode,
        )

    def _context_for(self, serial: str) -> dict[str, Any]:
        """Android/build/privilege context sent with the evidence; cached per device."""
        if self._tool_version is None:
            self._tool_version = adb_version(self._adb_path or "adb")
        if serial not in self._device_context:
            self._device_context[serial] = collect_safe_metadata(serial, self._adb_path)
        return self._device_context[serial]

    def _require_ready(self, serial: str) -> None:
        """The job's serial must be a currently ready device; nothing is guessed or substituted."""
        ready = {d.serial for d in detect_devices(self._adb_path) if d.status == "device"}
        if serial not in ready:
            raise AgentError("serial is not a ready device")

    def _failed_from_raw(self, message: dict[str, Any], error: str) -> dict[str, Any] | None:
        session_id, sequence = message.get("session_id"), message.get("sequence")
        operation, serial = message.get("operation"), message.get("serial")
        if not (isinstance(session_id, str) and isinstance(operation, str)):
            return None
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            return None
        return self._status(
            session_id,
            sequence,
            operation,
            serial if isinstance(serial, str) else None,
            error=error,
        )

    @staticmethod
    def _status(
        session_id: str,
        sequence: int,
        operation: str,
        serial: str | None,
        *,
        sha256_agent: str | None = None,
        size_bytes: int | None = None,
        returncode: int = -1,
        error: str | None = None,
    ) -> dict[str, Any]:
        return {
            "type": "job_status",
            "session_id": session_id,
            "sequence": sequence,
            "part": _PART,
            "parts_total": _PARTS_TOTAL,
            "operation": operation,
            "serial": serial,
            "sha256_agent": sha256_agent,
            "size_bytes": size_bytes,
            "returncode": returncode,
            "error": error,
        }
