import re

from src.device.adb_commands import (
    OPERATION_ARGS,
    OPERATION_PARAMETERS,
    OPERATION_PARTS,
    PACKAGE_NAME_PATTERN,
    RAW_SOURCE_LABEL,
)
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


def _reject(operation: str, reason: str, error: type[Exception]) -> None:
    audit("operation_rejected", reason, operation=operation, error_class=error.__name__)


def _check(operation: str, parameters: dict[str, str]) -> None:
    """Allowlist, mapping and parameter checks shared by single- and multi-part operations."""
    if operation not in ALLOWED_OPERATIONS:
        _reject(operation, "operation id is not allowlisted", OperationNotAllowedError)
        raise OperationNotAllowedError(f"operation {operation!r} is not allowlisted")
    if operation not in OPERATION_ARGS and operation not in OPERATION_PARTS:
        _reject(
            operation, "operation id is allowlisted but not mapped yet", OperationNotMappedError
        )
        raise OperationNotMappedError(f"operation {operation!r} has no adb mapping yet")
    required = OPERATION_PARAMETERS.get(operation, ())
    if set(parameters) != set(required):
        # Only the parameter names listed for the operation are accepted, nothing more or less.
        if not required:
            _reject(operation, "operation does not accept parameters", ValueError)
            raise ValueError(f"operation {operation!r} does not accept parameters")
        _reject(operation, "operation parameters do not match the allowed names", ValueError)
        raise ValueError(f"operation {operation!r} takes parameters {sorted(required)!r}")
    for name in required:
        if name == "package_name" and re.fullmatch(PACKAGE_NAME_PATTERN, parameters[name]) is None:
            _reject(operation, "parameter value has an invalid shape", ValueError)
            raise ValueError(f"parameter {name!r} of {operation!r} has an invalid shape")


def _fill(args: list[str], parameters: dict[str, str]) -> list[str]:
    filled = list(args)
    for name, value in parameters.items():
        filled = [value if arg == "{" + name + "}" else arg for arg in filled]
    return filled


def resolve_operation_parts(
    operation: str, parameters: dict[str, str]
) -> list[tuple[str, list[str]]]:
    """Ordered `(raw_source label, adb argument list)` per part. Anything else is rejected and
    audited; the arguments are the registered lists with only validated parameters filled in."""
    _check(operation, parameters)
    if operation in OPERATION_PARTS:
        return [(label, _fill(args, parameters)) for label, args in OPERATION_PARTS[operation]]
    return [(RAW_SOURCE_LABEL[operation], _fill(OPERATION_ARGS[operation], parameters))]


def resolve_operation(operation: str, parameters: dict[str, str]) -> list[str]:
    """The adb argument list of a single-command operation."""
    parts = resolve_operation_parts(operation, parameters)
    if len(parts) != 1:
        raise ValueError(f"operation {operation!r} has several parts; use resolve_operation_parts")
    return parts[0][1]
