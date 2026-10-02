import json
from pathlib import Path

import pytest

from src.acquisition.acquisition_profiles import PROFILES
from src.acquisition.command_allowlist import ALLOWED_OPERATIONS, resolve_operation
from src.device import adb_controller
from src.device.adb_commands import OPERATION_ARGS
from src.exceptions import OperationNotAllowedError, OperationNotMappedError

_MAPPED = {"collect_device_metadata", "collect_package_inventory"}


@pytest.fixture
def audit_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "audit.log"
    monkeypatch.setattr("src.state.audit_logger.AUDIT_LOG", path)
    return path


def _records(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_eight_allowed_two_mapped_six_not_mapped() -> None:
    assert len(ALLOWED_OPERATIONS) == 8
    assert set(OPERATION_ARGS) == _MAPPED
    assert len(ALLOWED_OPERATIONS - set(OPERATION_ARGS)) == 6


def test_mapped_operations_resolve_to_registered_argument_lists() -> None:
    assert resolve_operation("collect_device_metadata", {}) == ["shell", "getprop"]
    assert resolve_operation("collect_package_inventory", {}) == [
        "shell",
        "pm",
        "list",
        "packages",
        "-U",
    ]


def test_resolve_returns_a_copy_so_callers_cannot_mutate_the_allowlist() -> None:
    resolve_operation("collect_device_metadata", {}).append("; id")
    assert OPERATION_ARGS["collect_device_metadata"] == ["shell", "getprop"]


@pytest.mark.parametrize("operation", sorted(ALLOWED_OPERATIONS - _MAPPED))
def test_six_other_ids_stay_not_mapped(operation: str, audit_file: Path) -> None:
    with pytest.raises(OperationNotMappedError):
        resolve_operation(operation, {})
    assert _records(audit_file)[0]["error_class"] == "OperationNotMappedError"


def test_unknown_id_is_not_allowed_and_a_different_error_type(audit_file: Path) -> None:
    with pytest.raises(OperationNotAllowedError):
        resolve_operation("collect_everything", {})
    assert _records(audit_file)[0]["error_class"] == "OperationNotAllowedError"


@pytest.mark.parametrize("operation", sorted(_MAPPED))
def test_any_parameter_is_rejected_audited_and_never_reaches_adb(
    operation: str, audit_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def never(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("run_adb must not be reached")

    monkeypatch.setattr(adb_controller, "run_adb", never)

    with pytest.raises(ValueError, match="does not accept parameters"):
        resolve_operation(operation, {"extra": "; rm -rf /sdcard"})

    records = _records(audit_file)
    assert len(records) == 1
    assert records[0]["event"] == "operation_rejected"
    assert records[0]["error_class"] == "ValueError"
    assert "rm -rf" not in json.dumps(records[0])


def test_baseline_profile_lists_only_mapped_operation_ids() -> None:
    assert PROFILES["baseline_v030"] == ("collect_device_metadata", "collect_package_inventory")
    assert set(PROFILES["baseline_v030"]) <= set(OPERATION_ARGS)
