"""Runs one backend job: resolve the operation ID, run adb, write raw bytes, hash, report."""

import asyncio
import re
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from src.acquisition.availability import classify_failure, is_acquired
from src.acquisition.command_allowlist import resolve_operation_parts
from src.acquisition.evidence_writer import write_evidence
from src.device.adb_commands import APK_PATH_PATTERN
from src.device.adb_controller import AdbResult, adb_version, run_adb
from src.device.device_detection import collect_safe_metadata, detect_devices
from src.exceptions import AgentError
from src.integrity.hashing import sha256_file
from src.models import AcquisitionJob, AvailabilityStatus
from src.state.audit_logger import audit
from src.static_analysis.extractor import BUNDLE_FILES, extract
from src.transport.uploader import EvidenceUploader

RAW_ROOT = Path(__file__).resolve().parents[2] / "var" / "raw"
_PULL_OPERATION = "pull_subject_apk"
_PULL_PARTS_TOTAL = 2 + len(BUNDLE_FILES)  # path query, pulled file, bundle files
_PM_PATH_PREFIX = "package:"


def _failure_reason(exc: Exception) -> str:
    """Reason text for a job that could not run. Agent errors carry our own message; anything
    else (OS/parse errors) is reduced to its class name so no path or content leaks."""
    return str(exc)[:200] if isinstance(exc, AgentError) else type(exc).__name__


class AcquisitionRunner:
    """Executes jobs one at a time. Evidence goes to disk byte-exact before it is hashed.

    The job names its device (`serial`) and its position (`sequence`); the agent chooses neither.
    An operation with several commands runs them in order, one evidence file and one status per
    command (`part`), and stops after the first command that is not acquired: the backend marks
    the operation failed at that point and ignores later statuses for it.
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

    async def handle_job(self, message: dict[str, Any]) -> list[dict[str, Any]]:
        """The `job_status` messages to send, in order; empty when the job is too malformed."""
        return await asyncio.to_thread(self.run_job_parts, message)

    def run_job(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """The last status of the job, i.e. the one that decides the operation."""
        statuses = self.run_job_parts(message)
        return statuses[-1] if statuses else None

    def run_job_parts(self, message: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            job = AcquisitionJob(**message)
            uuid.UUID(job.session_id)  # the folder name comes from this value
        except (ValidationError, ValueError, TypeError) as exc:
            audit("job_rejected", "invalid job message", error_class=type(exc).__name__)
            status = self._failed_from_raw(message, type(exc).__name__)
            return [status] if status is not None else []

        try:
            parts = resolve_operation_parts(job.operation, job.parameters)
            self._require_ready(job.serial)
        except (AgentError, ValueError, OSError, KeyError) as exc:
            return [self._job_failed(job, exc)]

        if job.operation == _PULL_OPERATION:
            return self._run_pull_subject_apk(job, parts)

        statuses: list[dict[str, Any]] = []
        for part, (label, args) in enumerate(parts, start=1):
            status = self._run_part(job, part, len(parts), label, args)
            statuses.append(status)
            if status["availability_status"] != AvailabilityStatus.acquired.value:
                break
        return statuses

    def _run_part(
        self, job: AcquisitionJob, part: int, parts_total: int, label: str, args: list[str]
    ) -> dict[str, Any]:
        return self._run_adb_part(job, part, parts_total, label, args)[0]

    def _run_adb_part(
        self, job: AcquisitionJob, part: int, parts_total: int, label: str, args: list[str]
    ) -> tuple[dict[str, Any], AdbResult | None]:
        digest: str | None = None
        size: int | None = None
        try:
            result = run_adb(args, job.serial, adb_path=self._adb_path)
            acquired_at = datetime.now(UTC)
            name = f"{job.sequence}-{job.operation}-{part}.bin"
            path = self._raw_root / job.session_id / name
            size = write_evidence(path, result.stdout)
            digest = sha256_file(path)
            availability, reason = AvailabilityStatus.acquired, None
            if is_acquired(result):
                context = self._context_for(job.serial)
                self._uploader.upload(
                    path,
                    session_id=job.session_id,
                    operation_id=job.operation,
                    sequence=job.sequence,
                    part=part,
                    sha256_agent=digest,
                    size_bytes=size,
                    acquired_at=acquired_at,
                    raw_source=label,
                    tool_version=self._tool_version,
                    android_version=context.get("android_version"),
                    device_build=context.get("device_build"),
                    privilege_state=context.get("privilege_state"),
                )
            else:  # nothing usable to upload: report why (unsupported/denied/unavailable/failed)
                availability, reason = classify_failure(result)
        except (AgentError, ValueError, OSError, KeyError) as exc:
            # Keep the digest and size when the file exists locally but the upload failed.
            failed = self._job_failed(
                job, exc, part=part, parts_total=parts_total, digest=digest, size=size
            )
            return failed, None

        audit(
            "job_done",
            session_id=job.session_id,
            sequence=job.sequence,
            part=part,
            operation=job.operation,
            returncode=result.returncode,
            size_bytes=size,
            availability_status=availability.value,
        )
        status = self._status(
            job.session_id,
            job.sequence,
            job.operation,
            job.serial,
            part=part,
            parts_total=parts_total,
            sha256_agent=digest,
            size_bytes=size,
            returncode=result.returncode,
            availability=availability,
            reason=reason,
        )
        return status, result

    def _evidence_path(self, job: AcquisitionJob, part: int) -> Path:
        return self._raw_root / job.session_id / f"{job.sequence}-{job.operation}-{part}.bin"

    def _upload_file(
        self, job: AcquisitionJob, part: int, label: str, path: Path, acquired_at: datetime
    ) -> tuple[str, int]:
        """Hash an evidence file already on disk and upload it; returns (sha256, size)."""
        digest = sha256_file(path)
        size = path.stat().st_size
        context = self._context_for(job.serial)
        self._uploader.upload(
            path,
            session_id=job.session_id,
            operation_id=job.operation,
            sequence=job.sequence,
            part=part,
            sha256_agent=digest,
            size_bytes=size,
            acquired_at=acquired_at,
            raw_source=label,
            tool_version=self._tool_version,
            android_version=context.get("android_version"),
            device_build=context.get("device_build"),
            privilege_state=context.get("privilege_state"),
        )
        return digest, size

    def _acquired_status(
        self, job: AcquisitionJob, part: int, digest: str, size: int
    ) -> dict[str, Any]:
        audit(
            "job_done",
            session_id=job.session_id,
            sequence=job.sequence,
            part=part,
            operation=job.operation,
            returncode=0,
            size_bytes=size,
            availability_status=AvailabilityStatus.acquired.value,
        )
        return self._status(
            job.session_id,
            job.sequence,
            job.operation,
            job.serial,
            part=part,
            parts_total=_PULL_PARTS_TOTAL,
            sha256_agent=digest,
            size_bytes=size,
            returncode=0,
            availability=AvailabilityStatus.acquired,
        )

    def _run_pull_subject_apk(
        self, job: AcquisitionJob, parts: list[tuple[str, list[str]]]
    ) -> list[dict[str, Any]]:
        """Path query -> pull of the path the device itself reported -> static bundle.

        The APK path never comes from the backend: it is read from the output of part 1, must
        match the allowed shape and must be the only APK reported. The pulled file is evidence
        part 2; the bundle files are parts 3 onward. Execution stops at the first part that is
        not acquired.
        """
        total = _PULL_PARTS_TOTAL
        (path_label, path_args), (apk_label, pull_args) = parts

        status, result = self._run_adb_part(job, 1, total, path_label, path_args)
        statuses = [status]
        if result is None or status["availability_status"] != AvailabilityStatus.acquired.value:
            return statuses

        try:
            apk_path = self._apk_path_from(result)
        except AgentError as exc:
            return [*statuses, self._job_failed(job, exc, part=2, parts_total=total)]

        local = self._evidence_path(job, 2)
        digest: str | None = None
        size: int | None = None
        try:
            if local.exists():
                raise AgentError("evidence file already exists")
            local.parent.mkdir(parents=True, exist_ok=True)
            filled = [
                {"{apk_path}": apk_path, "{local_path}": str(local)}.get(arg, arg)
                for arg in pull_args
            ]
            pulled = run_adb(filled, job.serial, adb_path=self._adb_path)
            acquired_at = datetime.now(UTC)
            # `adb pull` reports on stderr and leaves stdout empty: success is the exit code
            # and a non-empty file at the evidence path, not output.
            pulled_ok = pulled.returncode == 0 and local.is_file() and local.stat().st_size > 0
            if not pulled_ok:
                availability, reason = classify_failure(pulled)
                statuses.append(
                    self._status(
                        job.session_id,
                        job.sequence,
                        job.operation,
                        job.serial,
                        part=2,
                        parts_total=total,
                        returncode=pulled.returncode,
                        availability=availability,
                        reason=reason,
                    )
                )
                return statuses
            digest, size = self._upload_file(job, 2, apk_label, local, acquired_at)
        except (AgentError, ValueError, OSError, KeyError) as exc:
            kept = local.is_file() and local.stat().st_size > 0
            return [
                *statuses,
                self._job_failed(
                    job,
                    exc,
                    part=2,
                    parts_total=total,
                    digest=sha256_file(local) if kept else None,
                    size=local.stat().st_size if kept else None,
                ),
            ]
        statuses.append(self._acquired_status(job, 2, digest, size))

        try:
            with tempfile.TemporaryDirectory(prefix="forplat-bundle-") as workdir:
                bundle = extract(local, Path(workdir) / "bundle")
                for part, source in enumerate(bundle, start=3):
                    evidence = self._evidence_path(job, part)
                    write_evidence(evidence, source.read_bytes())
                    digest, size = self._upload_file(
                        job, part, f"static:{source.name}", evidence, datetime.now(UTC)
                    )
                    statuses.append(self._acquired_status(job, part, digest, size))
        except (AgentError, ValueError, OSError, KeyError) as exc:
            statuses.append(self._job_failed(job, exc, part=len(statuses) + 1, parts_total=total))
        return statuses

    @staticmethod
    def _apk_path_from(result: AdbResult) -> str:
        """The single APK path the path query reported, validated; anything else is an error."""
        lines = [
            line.strip()
            for line in result.stdout.decode("utf-8", errors="replace").splitlines()
            if line.strip()
        ]
        if len(lines) != 1 or not lines[0].startswith(_PM_PATH_PREFIX):
            raise AgentError("the device did not report exactly one APK (split APKs not supported)")
        path = lines[0][len(_PM_PATH_PREFIX) :]
        if re.fullmatch(APK_PATH_PATTERN, path) is None or ".." in path.split("/"):
            raise AgentError("the reported APK path is not in an allowed location")
        return path

    def _job_failed(
        self,
        job: AcquisitionJob,
        exc: Exception,
        *,
        part: int = 1,
        parts_total: int = 1,
        digest: str | None = None,
        size: int | None = None,
    ) -> dict[str, Any]:
        audit(
            "job_failed",
            type(exc).__name__,
            session_id=job.session_id,
            sequence=job.sequence,
            part=part,
            operation=job.operation,
        )
        return self._status(
            job.session_id,
            job.sequence,
            job.operation,
            job.serial,
            part=part,
            parts_total=parts_total,
            sha256_agent=digest,
            size_bytes=size,
            error=type(exc).__name__,
            availability=AvailabilityStatus.failed,
            reason=_failure_reason(exc),
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
            availability=AvailabilityStatus.failed,
            reason=error,
        )

    @staticmethod
    def _status(
        session_id: str,
        sequence: int,
        operation: str,
        serial: str | None,
        *,
        part: int = 1,
        parts_total: int = 1,
        sha256_agent: str | None = None,
        size_bytes: int | None = None,
        returncode: int = -1,
        error: str | None = None,
        availability: AvailabilityStatus = AvailabilityStatus.failed,
        reason: str | None = None,
    ) -> dict[str, Any]:
        return {
            "type": "job_status",
            "session_id": session_id,
            "sequence": sequence,
            "part": part,
            "parts_total": parts_total,
            "operation": operation,
            "serial": serial,
            "sha256_agent": sha256_agent,
            "size_bytes": size_bytes,
            "returncode": returncode,
            "error": error,
            "availability_status": availability.value,
            "availability_reason": reason,
        }
