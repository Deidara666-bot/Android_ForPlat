"""Runs one backend job: resolve the operation ID, run adb, write raw bytes, hash, report."""

import asyncio
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.acquisition.command_allowlist import resolve_operation
from src.acquisition.evidence_writer import write_evidence
from src.device.adb_controller import run_adb
from src.device.device_detection import detect_devices
from src.exceptions import AgentError
from src.integrity.hashing import sha256_file
from src.models import AcquisitionJob
from src.state.audit_logger import audit

RAW_ROOT = Path(__file__).resolve().parents[2] / "var" / "raw"


class AcquisitionRunner:
    """Executes jobs one at a time. Evidence goes to disk byte-exact before it is hashed."""

    def __init__(self, adb_path: str | None = None, raw_root: Path | None = None) -> None:
        self._adb_path = adb_path
        self._raw_root = raw_root or RAW_ROOT
        # Jobs of one session arrive in order, so the Nth job of a session is sequence N.
        self._sequence: defaultdict[str, int] = defaultdict(int)

    async def handle_job(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Return the `job_status` message, or None when the job is too malformed to report."""
        return await asyncio.to_thread(self.run_job, message)

    def run_job(self, message: dict[str, Any]) -> dict[str, Any] | None:
        session_id, operation = message.get("session_id"), message.get("operation")
        try:
            job = AcquisitionJob(**message)
            uuid.UUID(job.session_id)  # the folder name comes from this value
        except (ValidationError, ValueError, TypeError) as exc:
            audit("job_rejected", "invalid job message", error_class=type(exc).__name__)
            if isinstance(session_id, str) and isinstance(operation, str):
                return self._failed(session_id, operation, type(exc).__name__)
            return None

        self._sequence[job.session_id] += 1
        sequence = self._sequence[job.session_id]
        try:
            args = resolve_operation(job.operation, job.parameters)
            serial = self._only_connected_serial()
            result = run_adb(args, serial, adb_path=self._adb_path)
            path = self._raw_root / job.session_id / f"{sequence}-{job.operation}.bin"
            size = write_evidence(path, result.stdout)
            digest = sha256_file(path)
        except (AgentError, ValueError, OSError) as exc:
            audit(
                "job_failed",
                type(exc).__name__,
                session_id=job.session_id,
                operation=job.operation,
            )
            return self._failed(job.session_id, job.operation, type(exc).__name__)

        audit(
            "job_done",
            session_id=job.session_id,
            operation=job.operation,
            sequence=sequence,
            returncode=result.returncode,
            size_bytes=size,
        )
        return {
            "type": "job_status",
            "session_id": job.session_id,
            "operation": job.operation,
            "sha256_agent": digest,
            "size_bytes": size,
            "returncode": result.returncode,
            "serial": serial,
        }

    def _only_connected_serial(self) -> str:
        """The job carries the backend device ID, not a serial: act only if exactly one device."""
        ready = [d.serial for d in detect_devices(self._adb_path) if d.status == "device"]
        if len(ready) != 1:
            raise AgentError(f"expected exactly one ready device, found {len(ready)}")
        return ready[0]

    @staticmethod
    def _failed(session_id: str, operation: str, error: str) -> dict[str, Any]:
        return {
            "type": "job_status",
            "session_id": session_id,
            "operation": operation,
            "sha256_agent": None,
            "size_bytes": None,
            "returncode": -1,
            "serial": None,
            "error": error,
        }
