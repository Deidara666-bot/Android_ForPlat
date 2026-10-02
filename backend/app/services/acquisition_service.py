from typing import Any

from app.core.constants import ALLOWED_OPERATIONS, MAPPED_OPERATIONS


class OperationNotAllowedError(ValueError):
    """The operation ID is not one of the eight allowlisted IDs."""


class OperationNotMappedError(ValueError):
    """The operation ID is allowlisted but the agent has no command mapped for it yet."""


class AcquisitionService:
    def build_job(self, session: Any, operation: str, parameters: dict[str, str]) -> dict[str, Any]:
        """Job payload for the agent: an operation ID and parameters, never a command string."""
        if operation not in ALLOWED_OPERATIONS:
            raise OperationNotAllowedError(f"operation {operation!r} is not allowlisted")
        if operation not in MAPPED_OPERATIONS:
            raise OperationNotMappedError(f"operation {operation!r} is not mapped yet")
        return {
            "type": "job",
            "session_id": str(session.id),
            "operation": operation,
            "case_id": str(session.case_id),
            "device_id": str(session.device_id),
            "parameters": dict(parameters),
        }
