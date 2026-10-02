import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import (
    ACQUISITION_PROFILES,
    ALLOWED_OPERATIONS,
    MAPPED_OPERATIONS,
    SessionStatus,
)
from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.agent import Agent
from app.models.device import Device
from app.schemas.acquisition import JobStatusIn

log = logging.getLogger(__name__)

_PENDING = "pending"
_COMPLETED = "completed"
_FAILED = "failed"


class OperationNotAllowedError(ValueError):
    """The operation ID is not one of the eight allowlisted IDs."""


class OperationNotMappedError(ValueError):
    """The operation ID is allowlisted but the agent has no command mapped for it yet."""


class UnknownProfileError(ValueError):
    """The requested acquisition profile does not exist."""


class AcquisitionService:
    def __init__(self, db: Session | None = None) -> None:
        self._db = db

    @staticmethod
    def validate_operation(operation: str) -> None:
        if operation not in ALLOWED_OPERATIONS:
            raise OperationNotAllowedError(f"operation {operation!r} is not allowlisted")
        if operation not in MAPPED_OPERATIONS:
            raise OperationNotMappedError(f"operation {operation!r} is not mapped yet")

    @staticmethod
    def operations_for(profile: str | None, operation: str | None) -> list[str]:
        """Operation IDs to run, validated. Exactly one of `profile` / `operation` is expected."""
        if profile is not None:
            if profile not in ACQUISITION_PROFILES:
                raise UnknownProfileError(f"profile {profile!r} does not exist")
            operations = list(ACQUISITION_PROFILES[profile])
        else:
            operations = [str(operation)]
        for item in operations:
            AcquisitionService.validate_operation(item)
        return operations

    def build_job(
        self,
        session: Any,
        operation_row: Any,
        serial: str,
        parameters: dict[str, str],
    ) -> dict[str, Any]:
        """Job payload for the agent (REF §API, 8 fields): identities and an operation ID,
        never a command string. `sequence` and `serial` come from the DB rows, not the client."""
        self.validate_operation(operation_row.operation_id)
        return {
            "type": "job",
            "session_id": str(session.id),
            "sequence": operation_row.sequence,
            "operation": operation_row.operation_id,
            "case_id": str(session.case_id),
            "device_id": str(session.device_id),
            "serial": serial,
            "parameters": dict(parameters),
        }

    def create_session(
        self,
        case_id: uuid.UUID,
        device: Device,
        agent: Agent,
        operations: list[str],
        profile: str | None,
    ) -> tuple[AcquisitionSession, list[AcquisitionOperation]]:
        assert self._db is not None
        session = AcquisitionSession(
            case_id=case_id,
            device_id=device.id,
            agent_id=agent.id,
            agent_version=agent.version,
            android_version=device.android_version,
            api_level=device.api_level,
            device_build=device.device_build,
            profile=profile,
            started_at=datetime.now(UTC),
            timezone="unknown",  # the device timezone is not collected yet; never guessed
            status=SessionStatus.running.value,
        )
        self._db.add(session)
        self._db.flush()
        rows = [
            AcquisitionOperation(session_id=session.id, sequence=index, operation_id=operation)
            for index, operation in enumerate(operations, start=1)
        ]
        self._db.add_all(rows)
        self._db.commit()
        return session, rows

    def get_session(self, session_id: uuid.UUID) -> AcquisitionSession | None:
        assert self._db is not None
        return self._db.get(AcquisitionSession, session_id)

    def list_operations(self, session_id: uuid.UUID) -> list[AcquisitionOperation]:
        assert self._db is not None
        return list(
            self._db.scalars(
                select(AcquisitionOperation)
                .where(AcquisitionOperation.session_id == session_id)
                .order_by(AcquisitionOperation.sequence)
            )
        )

    def mark_failed(self, session: AcquisitionSession, error: str) -> None:
        assert self._db is not None
        session.status = SessionStatus.failed.value
        session.ended_at = datetime.now(UTC)
        session.error = error
        self._db.commit()

    def apply_job_status(self, agent: Agent, status: JobStatusIn) -> bool:
        """Record one operation outcome. Only the agent that owns a running session may report."""
        assert self._db is not None
        session = self.get_session(status.session_id)
        if (
            session is None
            or session.agent_id != agent.id
            or session.status != SessionStatus.running.value
        ):
            log.warning("job_status for unknown or foreign session ignored")
            return False
        operation = self._db.scalar(
            select(AcquisitionOperation).where(
                AcquisitionOperation.session_id == session.id,
                AcquisitionOperation.operation_id == status.operation,
                AcquisitionOperation.status == _PENDING,
            )
        )
        if operation is None:
            log.warning("job_status for unknown or finished operation ignored")
            return False

        device = self._db.get(Device, session.device_id)
        serial_ok = device is not None and status.serial == device.serial
        operation.status = _COMPLETED if status.returncode == 0 and serial_ok else _FAILED

        operations = self.list_operations(session.id)
        if all(item.status != _PENDING for item in operations):
            failed = [item.operation_id for item in operations if item.status == _FAILED]
            session.ended_at = datetime.now(UTC)
            if failed:
                session.status = SessionStatus.failed.value
                session.error = "operation(s) failed: " + ", ".join(failed)
            else:
                session.status = SessionStatus.completed.value
        self._db.commit()
        return True
