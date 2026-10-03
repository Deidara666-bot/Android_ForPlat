import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from src.acquisition import acquisition_runner
from src.acquisition.acquisition_runner import AcquisitionRunner
from src.device.adb_controller import AdbResult
from src.device.device_detection import DetectedDevice
from src.exceptions import UploadError

_SESSION = "0f8b3c9e-6a4d-4b53-9c1e-2d7a5e8b1f60"
_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "package_inventory_sample.txt"


def _job(
    operation: str, sequence: int = 1, serial: str = "emulator-5554", **extra: Any
) -> dict[str, Any]:
    return {
        "type": "job",
        "session_id": _SESSION,
        "sequence": sequence,
        "operation": operation,
        "case_id": "c",
        "device_id": "d",
        "serial": serial,
        "parameters": {},
        **extra,
    }


class _FakeUploader:
    """Records uploads and the bytes on disk at that moment; can be told to fail."""

    def __init__(self) -> None:
        self.calls: list[tuple[Path, dict[str, Any], bytes]] = []
        self.fail = False

    def upload(self, path: Path, **fields: Any) -> None:
        self.calls.append((path, fields, path.read_bytes()))
        if self.fail:
            raise UploadError("rejected")


_UPLOADER = _FakeUploader()


@pytest.fixture(autouse=True)
def fresh_uploader(monkeypatch: pytest.MonkeyPatch) -> None:
    _UPLOADER.calls.clear()
    _UPLOADER.fail = False
    monkeypatch.setattr(acquisition_runner, "adb_version", lambda _path: "adb 1.0.41")
    monkeypatch.setattr(
        acquisition_runner,
        "collect_safe_metadata",
        lambda _serial, _adb=None: {
            "android_version": "16",
            "device_build": "BUILD",
            "privilege_state": "non_root",
        },
    )


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
    runner = AcquisitionRunner(_UPLOADER, raw_root=tmp_path)
    status = runner.run_job(_job("collect_package_inventory"))

    expected = _FIXTURE.read_bytes()
    written = tmp_path / _SESSION / "1-collect_package_inventory-1.bin"
    assert adb_calls == [(["shell", "pm", "list", "packages", "-U"], "emulator-5554")]
    assert written.read_bytes() == expected
    assert status == {
        "type": "job_status",
        "session_id": _SESSION,
        "sequence": 1,
        "part": 1,
        "parts_total": 1,
        "operation": "collect_package_inventory",
        "serial": "emulator-5554",
        "sha256_agent": hashlib.sha256(expected).hexdigest(),
        "size_bytes": len(expected),
        "returncode": 0,
        "error": None,
        "availability_status": "acquired",
        "availability_reason": None,
    }


def test_file_name_uses_the_sequence_carried_by_the_job(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    runner = AcquisitionRunner(_UPLOADER, raw_root=tmp_path)
    # Out of order on purpose: the agent must not number jobs by arrival.
    runner.run_job(_job("collect_package_inventory", sequence=2))
    runner.run_job(_job("collect_device_metadata", sequence=1))
    names = sorted(path.name for path in (tmp_path / _SESSION).iterdir())
    assert names == ["1-collect_device_metadata-1.bin", "2-collect_package_inventory-1.bin"]


def test_unmapped_operation_never_calls_adb_and_reports_failure(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(_job("collect_network_stats"))
    assert adb_calls == []
    assert status is not None
    assert status["returncode"] == -1
    assert status["error"] == "OperationNotMappedError"
    assert not (tmp_path / _SESSION).exists()


def test_parameters_are_refused_before_adb(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    job = _job("collect_device_metadata", parameters={"extra": "; id"})
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(job)
    assert adb_calls == []
    assert status is not None and status["error"] == "ValueError"


def test_session_id_that_is_not_a_uuid_cannot_choose_a_path(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    job = _job("collect_device_metadata")
    job["session_id"] = "../../evil"
    root = tmp_path / "raw"
    status = AcquisitionRunner(_UPLOADER, raw_root=root).run_job(job)
    assert adb_calls == []
    assert status is not None and status["returncode"] == -1
    assert not root.exists()
    assert not (tmp_path.parent / "evil").exists()


def test_extra_job_field_is_rejected(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(
        _job("collect_device_metadata", raw_command="rm -rf /")
    )
    assert adb_calls == []
    assert status is not None and status["error"] == "ValidationError"


def test_with_two_ready_devices_the_job_runs_on_its_own_serial(
    tmp_path: Path,
    adb_calls: list[tuple[list[str], str | None]],
    audit_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        acquisition_runner,
        "detect_devices",
        lambda _adb=None: [DetectedDevice("A", "device"), DetectedDevice("B", "device")],
    )
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(
        _job("collect_device_metadata", serial="B")
    )
    assert adb_calls == [(["shell", "getprop"], "B")]
    assert status is not None and status["serial"] == "B" and status["returncode"] == 0


def test_serial_that_is_not_connected_fails_without_calling_adb(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(
        _job("collect_device_metadata", serial="not-connected")
    )
    assert adb_calls == []
    assert status is not None
    assert status["returncode"] == -1
    assert status["serial"] == "not-connected"
    assert status["error"] == "AgentError"
    assert not (tmp_path / _SESSION).exists()


def test_serial_of_an_offline_device_is_not_ready(
    tmp_path: Path,
    adb_calls: list[tuple[list[str], str | None]],
    audit_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        acquisition_runner, "detect_devices", lambda _adb=None: [DetectedDevice("A", "offline")]
    )
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(
        _job("collect_device_metadata", serial="A")
    )
    assert adb_calls == []
    assert status is not None and status["returncode"] == -1


def test_option_like_serial_is_rejected_before_adb(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(
        _job("collect_device_metadata", serial="-d")
    )
    assert adb_calls == []
    assert status is not None and status["error"] == "ValidationError"


def test_job_without_a_usable_sequence_cannot_be_reported(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    job = _job("collect_device_metadata")
    del job["sequence"]
    assert AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(job) is None
    assert adb_calls == []


def test_audit_records_the_job_without_stdout(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(_job("collect_package_inventory"))
    records = [json.loads(line) for line in audit_file.read_text(encoding="utf-8").splitlines()]
    assert records[-1]["event"] == "job_done"
    assert "package:" not in json.dumps(records)


def test_upload_happens_after_hashing_with_the_exact_bytes_and_context(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(
        _job("collect_package_inventory", sequence=3)
    )
    assert len(_UPLOADER.calls) == 1
    path, fields, sent = _UPLOADER.calls[0]
    expected = _FIXTURE.read_bytes()
    assert path == tmp_path / _SESSION / "3-collect_package_inventory-1.bin"
    assert sent == expected
    assert fields["sha256_agent"] == hashlib.sha256(expected).hexdigest()
    assert fields["size_bytes"] == len(expected)
    assert (fields["sequence"], fields["part"]) == (3, 1)
    assert fields["operation_id"] == "collect_package_inventory"
    assert fields["raw_source"] == "pm list packages -U"
    assert fields["tool_version"] == "adb 1.0.41"
    assert fields["android_version"] == "16"
    assert fields["privilege_state"] == "non_root"
    assert fields["acquired_at"].tzinfo is not None


def test_rejected_upload_is_reported_as_failed_but_keeps_the_local_digest(
    tmp_path: Path, adb_calls: list[tuple[list[str], str | None]], audit_file: Path
) -> None:
    _UPLOADER.fail = True
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(
        _job("collect_package_inventory")
    )
    expected = _FIXTURE.read_bytes()
    assert status is not None
    assert status["returncode"] == -1
    assert status["error"] == "UploadError"
    assert status["sha256_agent"] == hashlib.sha256(expected).hexdigest()
    assert (tmp_path / _SESSION / "1-collect_package_inventory-1.bin").read_bytes() == expected


def test_failed_adb_command_is_not_uploaded_as_evidence(
    tmp_path: Path, audit_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(acquisition_runner, "run_adb", lambda *_a, **_k: AdbResult(b"", b"x", 1))
    monkeypatch.setattr(
        acquisition_runner,
        "detect_devices",
        lambda _adb=None: [DetectedDevice("emulator-5554", "device")],
    )
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(
        _job("collect_device_metadata")
    )
    assert _UPLOADER.calls == []
    assert status is not None and status["returncode"] == 1


def _patch_adb(monkeypatch: pytest.MonkeyPatch, result: AdbResult) -> None:
    monkeypatch.setattr(acquisition_runner, "run_adb", lambda *_a, **_k: result)
    monkeypatch.setattr(
        acquisition_runner,
        "detect_devices",
        lambda _adb=None: [DetectedDevice("emulator-5554", "device")],
    )


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        (AdbResult(b"", b"/system/bin/sh: foo: inaccessible or not found", 127), "unsupported"),
        (AdbResult(b"", b"java.lang.SecurityException: Permission Denial: x", 255), "denied"),
        (AdbResult(b"", b"", 0), "unavailable"),
        (AdbResult(b"", b"error: device offline", 1), "failed"),
    ],
)
def test_unusable_result_is_reported_with_status_and_reason_and_never_uploaded(
    tmp_path: Path,
    audit_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    result: AdbResult,
    expected: str,
) -> None:
    _patch_adb(monkeypatch, result)
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(
        _job("collect_device_metadata")
    )
    assert _UPLOADER.calls == []
    assert status is not None
    assert status["availability_status"] == expected
    assert status["availability_reason"]
    assert status["returncode"] == result.returncode


def test_exception_is_reported_as_failed_with_a_reason(
    tmp_path: Path, audit_file: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        acquisition_runner, "detect_devices", lambda _adb=None: [DetectedDevice("other", "device")]
    )
    status = AcquisitionRunner(_UPLOADER, raw_root=tmp_path).run_job(
        _job("collect_device_metadata")
    )
    assert status is not None
    assert status["availability_status"] == "failed"
    assert status["availability_reason"] == "serial is not a ready device"
