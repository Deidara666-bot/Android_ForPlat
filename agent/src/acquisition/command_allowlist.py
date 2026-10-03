import re

from src.device.adb_commands import OPERATION_ARGS, OPERATION_PARAMETERS, PACKAGE_NAME_PATTERN
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
    required = OPERATION_PARAMETERS.get(operation, ())
    if set(parameters) != set(required):
        # Only the parameter names listed for the operation are accepted, nothing more or less.
        reason = (
            "operation does not accept parameters"
            if not required
            else "operation parameters do not match the allowed names"
        )
        audit("operation_rejected", reason, operation=operation, error_class=ValueError.__name__)
        raise ValueError(
            f"operation {operation!r} does not accept parameters"
            if not required
            else f"operation {operation!r} takes parameters {sorted(required)!r}"
        )
    args = list(OPERATION_ARGS[operation])
    for name in required:
        value = parameters[name]
        if name == "package_name" and re.fullmatch(PACKAGE_NAME_PATTERN, value) is None:
            audit(
                "operation_rejected",
                "parameter value has an invalid shape",
                operation=operation,
                error_class=ValueError.__name__,
            )
            raise ValueError(f"parameter {name!r} of {operation!r} has an invalid shape")
        args = [value if arg == "{" + name + "}" else arg for arg in args]
    return args
