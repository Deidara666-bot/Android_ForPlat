import json
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.acquisition.command_allowlist import ALLOWED_OPERATIONS, resolve_operation
from src.device import adb_controller
from src.device.privilege_detector import detect_privilege
from src.exceptions import OperationNotAllowedError, OperationNotMappedError
from src.models import AcquisitionJob, PrivilegeState


@pytest.fixture
def audit_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "audit.log"
    monkeypatch.setattr("src.state.audit_logger.AUDIT_LOG", path)
    return path


def _lines(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_exactly_eight_allowed_operations() -> None:
    assert len(ALLOWED_OPERATIONS) == 8


@pytest.mark.parametrize(
    "operation",
    ["adb shell pm uninstall x", "", "collect_everything", "shell", "collect_package_inventory;id"],
)
def test_unknown_operation_is_not_allowed_and_audited(operation: str, audit_file: Path) -> None:
    with pytest.raises(OperationNotAllowedError):
        resolve_operation(operation, {})
    records = _lines(audit_file)
    assert len(records) == 1
    assert records[0]["event"] == "operation_rejected"
    assert records[0]["operation"] == operation
    assert records[0]["error_class"] == "OperationNotAllowedError"


@pytest.mark.parametrize(
    "operation",
    sorted(
        ALLOWED_OPERATIONS
        - {
            "collect_device_metadata",
            "collect_package_inventory",
            "collect_package_detail",
            "collect_accessibility_state",
        }
    ),
)
def test_allowed_but_unmapped_operation_is_not_mapped_and_audited(
    operation: str, audit_file: Path
) -> None:
    with pytest.raises(OperationNotMappedError):
        resolve_operation(operation, {})
    records = _lines(audit_file)
    assert len(records) == 1
    assert records[0]["error_class"] == "OperationNotMappedError"


def test_the_two_errors_are_distinct_types() -> None:
    assert not issubclass(OperationNotAllowedError, OperationNotMappedError)
    assert not issubclass(OperationNotMappedError, OperationNotAllowedError)


def test_job_with_extra_field_is_rejected() -> None:
    fields = {
        "type": "job",
        "session_id": "s",
        "sequence": 1,
        "operation": "collect_package_inventory",
        "case_id": "c",
        "device_id": "d",
        "serial": "emulator-5554",
        "parameters": {},
    }
    AcquisitionJob(**fields)  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        AcquisitionJob(**fields, raw_command="rm -rf /")  # type: ignore[arg-type]


def _fake_run(stdout: bytes, returncode: int = 0) -> object:
    calls: list[dict[str, object]] = []

    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[bytes]:
        calls.append({"command": command, **kwargs})
        return subprocess.CompletedProcess(command, returncode, stdout, b"")

    run.calls = calls  # type: ignore[attr-defined]
    return run


@pytest.mark.parametrize(
    ("stdout", "expected"),
    [
        (b"uid=0(root) gid=0(root) groups=0(root)\n", PrivilegeState.root_detected),
        (b"uid=2000(shell) gid=2000(shell) groups=2000(shell)\n", PrivilegeState.non_root),
        (b"unexpected output\n", PrivilegeState.unknown),
    ],
)
def test_privilege_detector_reads_uid(
    monkeypatch: pytest.MonkeyPatch, stdout: bytes, expected: PrivilegeState
) -> None:
    monkeypatch.setattr(adb_controller.subprocess, "run", _fake_run(stdout))
    assert detect_privilege("emulator-5554", adb_path="adb") == expected


def test_privilege_detector_unknown_on_adb_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(adb_controller.subprocess, "run", _fake_run(b"", returncode=1))
    assert detect_privilege(adb_path="adb") == PrivilegeState.unknown

    def boom(*_args: object, **_kwargs: object) -> None:
        raise FileNotFoundError

    monkeypatch.setattr(adb_controller.subprocess, "run", boom)
    assert detect_privilege(adb_path="adb") == PrivilegeState.unknown


def test_adb_is_run_with_an_argument_list_and_no_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _fake_run(b"uid=2000(shell)\n")
    monkeypatch.setattr(adb_controller.subprocess, "run", fake)
    detect_privilege("emulator-5554", adb_path="adb")
    call = fake.calls[0]  # type: ignore[attr-defined]
    assert call["command"] == ["adb", "-s", "emulator-5554", "shell", "id"]
    assert call["shell"] is False


def _job_fields(**overrides: object) -> dict[str, object]:
    return {
        "type": "job",
        "session_id": "s",
        "sequence": 1,
        "operation": "collect_package_inventory",
        "case_id": "c",
        "device_id": "d",
        "serial": "emulator-5554",
        "parameters": {},
        **overrides,
    }


@pytest.mark.parametrize("serial", ["-d", "-e", "a b", "x;y", "", "a" * 65, "$(id)", "a\nb"])
def test_job_serial_that_could_be_an_adb_option_or_shell_text_is_rejected(serial: str) -> None:
    with pytest.raises(ValidationError):
        AcquisitionJob(**_job_fields(serial=serial))  # type: ignore[arg-type]


@pytest.mark.parametrize("serial", ["emulator-5554", "192.168.1.5:5555", "R58M12ABCDE", "a_b.c"])
def test_job_serial_of_a_real_device_is_accepted(serial: str) -> None:
    assert AcquisitionJob(**_job_fields(serial=serial)).serial == serial  # type: ignore[arg-type]


@pytest.mark.parametrize("sequence", [0, -1])
def test_job_sequence_below_one_is_rejected(sequence: int) -> None:
    with pytest.raises(ValidationError):
        AcquisitionJob(**_job_fields(sequence=sequence))  # type: ignore[arg-type]


@pytest.mark.parametrize("missing", ["sequence", "serial"])
def test_job_without_sequence_or_serial_is_rejected(missing: str) -> None:
    fields = _job_fields()
    del fields[missing]
    with pytest.raises(ValidationError):
        AcquisitionJob(**fields)  # type: ignore[arg-type]
