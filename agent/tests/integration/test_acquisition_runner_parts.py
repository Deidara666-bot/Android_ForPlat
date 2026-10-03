"""Multi-command operations: one evidence file and one status per command (`part`)."""

import hashlib
from pathlib import Path
from typing import Any

import pytest

from src.acquisition import acquisition_runner
from src.acquisition.acquisition_runner import AcquisitionRunner
from src.device.adb_controller import AdbResult
from src.device.device_detection import DetectedDevice
from src.exceptions import UploadError

_SESSION = "0f8b3c9e-6a4d-4b53-9c1e-2d7a5e8b1f60"
_A11Y = (
    b"com.google.android.marvin.talkback/"
    b"com.google.android.accessibility.selecttospeak.SelectToSpeakService\n"
)
_APPOPS = b"No operations.\nDefault mode: default\n"


class _FakeUploader:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, dict[str, Any], bytes]] = []

    def upload(self, path: Path, **fields: Any) -> None:
        self.calls.append((path, fields, path.read_bytes()))


def _job(**extra: Any) -> dict[str, Any]:
    return {
        "type": "job",
        "session_id": _SESSION,
        "sequence": 3,
        "operation": "collect_accessibility_state",
        "case_id": "c",
        "device_id": "d",
        "serial": "emulator-5554",
        "parameters": {"package_name": "com.x.y"},
        **extra,
    }


@pytest.fixture
def uploader() -> _FakeUploader:
    return _FakeUploader()


@pytest.fixture(autouse=True)
def environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("src.state.audit_logger.AUDIT_LOG", tmp_path / "audit.log")
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
    monkeypatch.setattr(
        acquisition_runner,
        "detect_devices",
        lambda _adb=None: [DetectedDevice("emulator-5554", "device")],
    )


def _fake_adb(monkeypatch: pytest.MonkeyPatch, results: list[AdbResult]) -> list[list[str]]:
    calls: list[list[str]] = []

    def fake(args: list[str], serial: str | None = None, **_: object) -> AdbResult:
        calls.append(args)
        return results[len(calls) - 1]

    monkeypatch.setattr(acquisition_runner, "run_adb", fake)
    return calls


def test_three_parts_write_three_files_and_report_three_statuses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, uploader: _FakeUploader
) -> None:
    results = [AdbResult(_A11Y, b"", 0), AdbResult(b"null\n", b"", 0), AdbResult(_APPOPS, b"", 0)]
    calls = _fake_adb(monkeypatch, results)
    statuses = AcquisitionRunner(uploader, raw_root=tmp_path).run_job_parts(_job())  # type: ignore[arg-type]

    names = sorted(p.name for p in (tmp_path / _SESSION).iterdir())
    assert names == [f"3-collect_accessibility_state-{n}.bin" for n in (1, 2, 3)]
    assert [(s["part"], s["parts_total"]) for s in statuses] == [(1, 3), (2, 3), (3, 3)]
    assert {s["availability_status"] for s in statuses} == {"acquired"}
    assert calls[0][-1] == "enabled_accessibility_services"
    assert calls[1][-1] == "enabled_notification_listeners"
    assert calls[2][2:] == ["get", "com.x.y", "SYSTEM_ALERT_WINDOW"]
    assert [fields["part"] for _, fields, _ in uploader.calls] == [1, 2, 3]
    assert [fields["raw_source"] for _, fields, _ in uploader.calls] == [
        "settings secure a11y",
        "settings secure nls",
        "appops overlay",
    ]
    for _path, fields, on_disk in uploader.calls:  # byte-exact and hashed per part
        assert fields["sha256_agent"] == hashlib.sha256(on_disk).hexdigest()
        assert fields["sequence"] == 3
    assert [on_disk for _, _, on_disk in uploader.calls] == [r.stdout for r in results]


def test_every_part_runs_and_reports_even_after_a_part_that_is_not_acquired(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, uploader: _FakeUploader
) -> None:
    results = [
        AdbResult(b"null\n", b"", 0),
        AdbResult(b"", b"Permission denial: not allowed\n", 255),
        AdbResult(_APPOPS, b"", 0),
    ]
    calls = _fake_adb(monkeypatch, results)
    statuses = AcquisitionRunner(uploader, raw_root=tmp_path).run_job_parts(_job())  # type: ignore[arg-type]
    assert [s["availability_status"] for s in statuses] == ["acquired", "denied", "acquired"]
    assert [s["part"] for s in statuses] == [1, 2, 3]
    assert [s["raw_source"] for s in statuses] == [
        "settings secure a11y",
        "settings secure nls",
        "appops overlay",
    ]
    assert len(calls) == 3  # part 3 ran: its source does not depend on part 2
    assert [fields["part"] for _, fields, _ in uploader.calls] == [1, 3]  # acquired parts only


def test_a_failed_upload_marks_only_its_part_and_the_rest_still_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class RejectingFirst(_FakeUploader):
        def upload(self, path: Path, **fields: Any) -> None:
            super().upload(path, **fields)
            if fields["part"] == 1:
                raise UploadError("rejected")

    calls = _fake_adb(monkeypatch, [AdbResult(b"null\n", b"", 0)] * 3)
    uploader = RejectingFirst()
    statuses = AcquisitionRunner(uploader, raw_root=tmp_path).run_job_parts(_job())  # type: ignore[arg-type]
    assert [s["availability_status"] for s in statuses] == ["failed", "acquired", "acquired"]
    assert statuses[0]["part"] == 1 and statuses[0]["error"] == "UploadError"
    assert statuses[0]["raw_source"] == "settings secure a11y"
    assert len(calls) == 3


def test_bad_parameter_runs_no_part_at_all(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, uploader: _FakeUploader
) -> None:
    calls = _fake_adb(monkeypatch, [])
    statuses = AcquisitionRunner(uploader, raw_root=tmp_path).run_job_parts(  # type: ignore[arg-type]
        _job(parameters={"package_name": "com.x; id"})
    )
    assert calls == []
    assert [s["availability_status"] for s in statuses] == ["failed"]
    assert statuses[0]["error"] == "ValueError"


def test_run_job_returns_the_last_status() -> None:
    runner = AcquisitionRunner(_FakeUploader())  # type: ignore[arg-type]
    assert runner.run_job({"type": "nope"}) is None
