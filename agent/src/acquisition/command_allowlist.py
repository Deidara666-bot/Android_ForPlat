from src.device.adb_commands import OPERATION_ARGS
from src.exceptions import OperationNotAllowedError, OperationNotMappedError
from src.state.audit_logger import audit

ALLOWED_OPERATIONS: frozenset[str] = frozenset(
    {
        "collect_device_metadata",
        "collect_package_inventory",
        "collect_package_detail",
        "collect_usage_state",
        "collect_accessibility_state",
        "collect_sensitive_provider_data",
        "collect_network_stats",
        "pull_subject_apk",
    }
)


def resolve_operation(operation: str, parameters: dict[str, str]) -> list[str]:
    """Map an operation ID to its adb argument list. Anything else is rejected and audited."""
    if operation not in ALLOWED_OPERATIONS:
        audit(
            "operation_rejected",
            "operation id is not allowlisted",
            operation=operation,
            error_class=OperationNotAllowedError.__name__,
        )
        raise OperationNotAllowedError(f"operation {operation!r} is not allowlisted")
    if operation not in OPERATION_ARGS:
        audit(
            "operation_rejected",
            "operation id is allowlisted but not mapped yet",
            operation=operation,
            error_class=OperationNotMappedError.__name__,
        )
        raise OperationNotMappedError(f"operation {operation!r} has no adb mapping yet")
    return list(OPERATION_ARGS[operation])
