import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from src.acquisition import acquisition_runner
from src.acquisition.acquisition_runner import AcquisitionRunner
from src.device.adb_controller import AdbResult
from src.device.device_detection import DetectedDevice

_SESSION = "0f8b3c9e-6a4d-4b53-9c1e-2d7a5e8b1f60"
_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "package_inventory_sample.txt"


def _job(operation: str, **extra: Any) -> dict[str, Any]:
    return {
        "type": "job",
        "session_id": _SESSION,
        "operation": operation,
        "case_id": "c",
        "device_id": "d",
        "parameters": {},
        **extra,
    }


@pytest.fixture
def audit_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    path = tmp_path / "audit.log"
    monkeypatch.setattr("src.state.audit_logger.AUDIT_LOG", path)
    return path


@pytest.fixture
def adb_calls(monkeypatch: pytest.MonkeyPatch) -> list[tuple[list[str], str | None]]:
    """Replace `run_adb` (the only process spawner) with a recorder returning fixture bytes."""
    calls: list[tuple[list[str], str | None]] = []
    stdout_by_args = {"getprop": b"[ro.build.version.sdk]: [36]\r\n", "pm": _FIXTURE.read_bytes()}

    def fake(args: list[str], serial: str | None = None, **_: object) -> AdbResult:
        calls.append((args, serial))
        return AdbResult(stdout_by_args[args[1]], b"", 0)

    monkeypatch.setattr(acquisition_runner, "run_adb", fake)
    monkeypatch.setattr(
        acquisition_runner,
        "detect_devices",
        lambda _adb=None: [DetectedDevice("emulator-5554", "device")],
    )
    return calls


def test_job_runs_adb_writes_bytes_exactly_and_reports_hash(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    runner = AcquisitionRunner(raw_root=tmp_path)
    status = runner.run_job(_job("collect_package_inventory"))

    expected = _FIXTURE.read_bytes()
    written = tmp_path / _SESSION / "1-collect_package_inventory.bin"
    assert adb_calls == [(["shell", "pm", "list", "packages", "-U"], "emulator-5554")]
    assert written.read_bytes() == expected
    assert status == {
        "type": "job_status",
        "session_id": _SESSION,
        "operation": "collect_package_inventory",
        "sha256_agent": hashlib.sha256(expected).hexdigest(),
        "size_bytes": len(expected),
        "returncode": 0,
        "serial": "emulator-5554",
    }


def test_two_jobs_of_one_session_get_sequence_one_and_two(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    runner = AcquisitionRunner(raw_root=tmp_path)
    runner.run_job(_job("collect_device_metadata"))
    runner.run_job(_job("collect_package_inventory"))
    names = sorted(path.name for path in (tmp_path / _SESSION).iterdir())
    assert names == ["1-collect_device_metadata.bin", "2-collect_package_inventory.bin"]


def test_unmapped_operation_never_calls_adb_and_reports_failure(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    status = AcquisitionRunner(raw_root=tmp_path).run_job(_job("collect_usage_state"))
    assert adb_calls == []
    assert status is not None
    assert status["returncode"] == -1
    assert status["error"] == "OperationNotMappedError"
    assert not (tmp_path / _SESSION).exists()


def test_parameters_are_refused_before_adb(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    job = _job("collect_device_metadata", parameters={"extra": "; id"})
    status = AcquisitionRunner(raw_root=tmp_path).run_job(job)
    assert adb_calls == []
    assert status is not None and status["error"] == "ValueError"


def test_session_id_that_is_not_a_uuid_cannot_choose_a_path(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    job = _job("collect_device_metadata")
    job["session_id"] = "../../evil"
    root = tmp_path / "raw"
    status = AcquisitionRunner(raw_root=root).run_job(job)
    assert adb_calls == []
    assert status is not None and status["returncode"] == -1
    assert not root.exists()
    assert not (tmp_path.parent / "evil").exists()


def test_extra_job_field_is_rejected(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    status = AcquisitionRunner(raw_root=tmp_path).run_job(
        _job("collect_device_metadata", raw_command="rm -rf /")
    )
    assert adb_calls == []
    assert status is not None and status["error"] == "ValidationError"


def test_two_ready_devices_is_refused(
    tmp_path: Path,
    adb_calls: list[tuple[list[str], str | None]],
    audit_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        acquisition_runner,
        "detect_devices",
        lambda _adb=None: [DetectedDevice("a", "device"), DetectedDevice("b", "device")],
    )
    status = AcquisitionRunner(raw_root=tmp_path).run_job(_job("collect_device_metadata"))
    assert adb_calls == []
    assert status is not None and status["returncode"] == -1


def test_audit_records_the_job_without_stdout(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    AcquisitionRunner(raw_root=tmp_path).run_job(_job("collect_package_inventory"))
    records = [json.loads(line) for line in audit_file.read_text(encoding="utf-8").splitlines()]
    assert records[-1]["event"] == "job_done"
    assert "package:" not in json.dumps(records)
