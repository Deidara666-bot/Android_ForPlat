"""`pull_subject_apk`: paths from the device's own output, one pull per APK, then the bundle."""

import hashlib
from pathlib import Path
from typing import Any

import pytest

from src.acquisition import acquisition_runner
from src.acquisition.acquisition_runner import AcquisitionRunner
from src.acquisition.command_allowlist import resolve_operation_parts
from src.device import adb_commands
from src.device.adb_controller import AdbResult, run_adb
from src.device.device_detection import DetectedDevice
from src.exceptions import UploadError
from src.static_analysis.extractor import BUNDLE_FILES, ExtractorError

_SESSION = "0f8b3c9e-6a4d-4b53-9c1e-2d7a5e8b1f60"
_APK_BYTES = b"PK\x03\x04 pretend apk bytes"
_PATH = "/system/app/Stk/Stk.apk"
_BUNDLE = len(BUNDLE_FILES)
_BUNDLE_LABELS = [f"static:{name}" for name in BUNDLE_FILES]


def _pm(*paths: str) -> bytes:
    return b"".join(f"package:{path}\r\n".encode() for path in paths)


_SPLITS = (
    "/data/app/~~x==/com.x-y==/split_config.xxhdpi.apk",
    "/data/app/~~x==/com.x-y==/base.apk",
    "/data/app/~~x==/com.x-y==/split_config.arm64_v8a.apk",
)


def _job(**extra: Any) -> dict[str, Any]:
    return {
        "type": "job",
        "session_id": _SESSION,
        "sequence": 2,
        "operation": "pull_subject_apk",
        "case_id": "c",
        "device_id": "d",
        "serial": "emulator-5554",
        "parameters": {"package_name": "com.android.stk"},
        **extra,
    }


class _Uploader:
    def __init__(self) -> None:
        self.calls: list[tuple[dict[str, Any], bytes]] = []
        self.fail_part: int | None = None

    def upload(self, path: Path, **fields: Any) -> None:
        self.calls.append((fields, path.read_bytes()))
        if fields["part"] == self.fail_part:
            raise UploadError("rejected")


class _Device:
    """Fake adb: answers `pm path` and writes the pulled files like `adb pull` does."""

    def __init__(self) -> None:
        self.pm_output = _pm(_PATH)
        # like the real tool: the summary goes to stderr, stdout stays empty
        self.pull_result = AdbResult(b"", b"/x.apk: 1 file pulled, 0 skipped.\n", 0)
        self.fail_pull_of: str | None = None  # device path whose pull fails
        self.writes_file = True
        self.calls: list[list[str]] = []

    def __call__(self, args: list[str], serial: str | None = None, **_: object) -> AdbResult:
        self.calls.append(args)
        if args[:2] == ["shell", "pm"]:
            return AdbResult(self.pm_output, b"", 0)
        if args[0] == "pull":
            if args[1] == self.fail_pull_of:
                return AdbResult(b"", b"adb: error: failed to stat remote object\n", 1)
            if self.pull_result.returncode == 0 and self.writes_file:
                Path(args[2]).write_bytes(_APK_BYTES + args[1].encode())
            return self.pull_result
        raise AssertionError(f"unexpected adb call {args}")


@pytest.fixture
def uploader() -> _Uploader:
    return _Uploader()


@pytest.fixture
def extract_calls() -> list[list[tuple[str, Path]]]:
    return []


@pytest.fixture
def device(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, extract_calls: list[list[tuple[str, Path]]]
) -> _Device:
    fake = _Device()
    monkeypatch.setattr("src.state.audit_logger.AUDIT_LOG", tmp_path / "audit.log")
    monkeypatch.setattr(acquisition_runner, "run_adb", fake)
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

    def fake_extract(apks: list[tuple[str, Path]], out_dir: Path) -> list[Path]:
        extract_calls.append(list(apks))
        assert all(path.is_file() for _, path in apks)
        out_dir.mkdir(parents=True)
        paths = []
        for name in BUNDLE_FILES:
            path = out_dir / name
            path.write_bytes(f"content of {name}\n".encode())
            paths.append(path)
        return paths

    monkeypatch.setattr(acquisition_runner, "extract", fake_extract)
    return fake


def _run(tmp_path: Path, uploader: _Uploader, **extra: Any) -> list[dict[str, Any]]:
    return AcquisitionRunner(uploader, raw_root=tmp_path).run_job_parts(_job(**extra))  # type: ignore[arg-type]


def _labels(*apk_names: str) -> list[str]:
    return ["pm path", *[f"apk file:{name}" for name in apk_names], *_BUNDLE_LABELS]


def _assert_blocked_by(statuses: list[dict[str, Any]], first: int, prerequisite: int) -> None:
    """Parts `first`.. are failed, name their prerequisite and carry their own raw_source."""
    blocked = [s for s in statuses if s["part"] >= first]
    assert [s["part"] for s in blocked] == list(range(first, len(statuses) + 1))
    assert {s["availability_status"] for s in blocked} == {"failed"}
    assert {s["availability_reason"] for s in blocked} == {
        f"prasyarat part {prerequisite} tidak diperoleh"
    }


def test_a_single_apk_gives_part_1_one_pull_and_the_bundle_parts(
    tmp_path: Path, device: _Device, uploader: _Uploader, extract_calls: list[Any]
) -> None:
    statuses = _run(tmp_path, uploader)
    total = 2 + _BUNDLE
    assert [(s["part"], s["parts_total"]) for s in statuses] == [
        (n, total) for n in range(1, total + 1)
    ]
    assert {s["availability_status"] for s in statuses} == {"acquired"}
    assert [s["raw_source"] for s in statuses] == _labels("Stk.apk")
    assert [fields["part"] for fields, _ in uploader.calls] == list(range(1, total + 1))
    names = sorted(p.name for p in (tmp_path / _SESSION).iterdir())
    assert names == sorted(f"2-pull_subject_apk-{n}.bin" for n in range(1, total + 1))
    for fields, data in uploader.calls:  # every part hashed from the bytes that were uploaded
        assert fields["sha256_agent"] == hashlib.sha256(data).hexdigest()
        assert fields["sequence"] == 2 and fields["size_bytes"] == len(data)
    assert uploader.calls[1][1] == _APK_BYTES + _PATH.encode()  # part 2 is the APK itself
    assert uploader.calls[2][1] == f"content of {BUNDLE_FILES[0]}\n".encode()
    assert [name for name, _ in extract_calls[0]] == ["Stk.apk"]


def test_three_apk_lines_give_three_apk_parts_base_first_then_the_bundle(
    tmp_path: Path, device: _Device, uploader: _Uploader, extract_calls: list[Any]
) -> None:
    device.pm_output = _pm(*_SPLITS)
    statuses = _run(tmp_path, uploader)
    total = 1 + 3 + _BUNDLE
    assert [(s["part"], s["parts_total"]) for s in statuses] == [
        (n, total) for n in range(1, total + 1)
    ]
    assert {s["availability_status"] for s in statuses} == {"acquired"}
    assert [s["raw_source"] for s in statuses] == _labels(
        "base.apk", "split_config.arm64_v8a.apk", "split_config.xxhdpi.apk"
    )
    pulls = [call[1] for call in device.calls if call[0] == "pull"]
    assert [path.rsplit("/", 1)[-1] for path in pulls] == [
        "base.apk",
        "split_config.arm64_v8a.apk",
        "split_config.xxhdpi.apk",
    ]
    assert [name for name, _ in extract_calls[0]] == [
        "base.apk",
        "split_config.arm64_v8a.apk",
        "split_config.xxhdpi.apk",
    ]
    assert extract_calls[0][0][1] == tmp_path / _SESSION / "2-pull_subject_apk-2.bin"


def test_each_pull_uses_a_path_the_device_reported_and_its_own_evidence_path(
    tmp_path: Path, device: _Device, uploader: _Uploader
) -> None:
    device.pm_output = _pm(*_SPLITS)
    _run(tmp_path, uploader)
    assert device.calls[0] == ["shell", "pm", "path", "com.android.stk"]
    pulls = [call for call in device.calls if call[0] == "pull"]
    assert {call[1] for call in pulls} == set(_SPLITS)
    for index, call in enumerate(pulls):
        assert Path(call[2]) == tmp_path / _SESSION / f"2-pull_subject_apk-{2 + index}.bin"
    assert all("{" not in arg for call in device.calls for arg in call)


@pytest.mark.parametrize(
    "output",
    [
        _pm("/sdcard/evil.apk"),
        _pm("/data/local/tmp/x.apk"),
        _pm("/system/app/a b/x.apk"),
        _pm("/system/app/Stk/Stk.txt"),
        _pm("relative/x.apk"),
        _pm("/system/../data/x.apk"),
        _pm("/system/app/../../data/app/x/base.apk"),
        _pm("/system/a.apk", "/system/../b.apk"),  # one bad line refuses the whole list
        _pm("/data/app/a/base.apk", "/data/app/b/base.apk"),  # two files with the same name
        _pm("/system/app/we ird.apk"),
        b"/system/a.apk\n",
        b"no package line\n",
    ],
)
def test_a_list_that_is_not_all_allowed_apks_runs_no_pull_and_blocks_the_rest(
    tmp_path: Path, device: _Device, uploader: _Uploader, output: bytes
) -> None:
    device.pm_output = output
    statuses = _run(tmp_path, uploader)
    total = 2 + _BUNDLE
    assert [s["part"] for s in statuses] == list(range(1, total + 1))
    assert [(s["part"], s["availability_status"]) for s in statuses[:2]] == [
        (1, "acquired"),
        (2, "failed"),
    ]
    assert statuses[1]["raw_source"] == "apk file"  # S is unknown: one generic APK part
    _assert_blocked_by(statuses, 3, 2)
    assert not any(call[0] == "pull" for call in device.calls)
    assert [fields["part"] for fields, _ in uploader.calls] == [1]


def test_a_failed_pull_is_classified_and_blocks_the_bundle_parts(
    tmp_path: Path, device: _Device, uploader: _Uploader
) -> None:
    device.pull_result = AdbResult(
        b"", b"adb: error: failed to stat remote object: No such file\n", 1
    )
    statuses = _run(tmp_path, uploader)
    assert [(s["part"], s["availability_status"]) for s in statuses[:2]] == [
        (1, "acquired"),
        (2, "failed"),
    ]
    _assert_blocked_by(statuses, 3, 2)
    assert statuses[1]["returncode"] == 1
    assert [fields["part"] for fields, _ in uploader.calls] == [1]


def test_one_failed_split_still_pulls_the_others_but_blocks_the_bundle(
    tmp_path: Path, device: _Device, uploader: _Uploader, extract_calls: list[Any]
) -> None:
    device.pm_output = _pm(*_SPLITS)
    device.fail_pull_of = "/data/app/~~x==/com.x-y==/split_config.arm64_v8a.apk"
    statuses = _run(tmp_path, uploader)
    assert [s["availability_status"] for s in statuses[:4]] == [
        "acquired",
        "acquired",  # base.apk
        "failed",  # split_config.arm64_v8a.apk (part 3)
        "acquired",  # split_config.xxhdpi.apk is still pulled
    ]
    _assert_blocked_by(statuses, 5, 3)
    assert [s["raw_source"] for s in statuses] == _labels(
        "base.apk", "split_config.arm64_v8a.apk", "split_config.xxhdpi.apk"
    )
    assert [fields["part"] for fields, _ in uploader.calls] == [1, 2, 4]
    assert extract_calls == []  # no bundle without every APK part


def test_a_rejected_apk_upload_blocks_the_bundle_and_keeps_the_local_digest(
    tmp_path: Path, device: _Device, uploader: _Uploader
) -> None:
    uploader.fail_part = 2
    statuses = _run(tmp_path, uploader)
    assert [(s["part"], s["availability_status"]) for s in statuses[:2]] == [
        (1, "acquired"),
        (2, "failed"),
    ]
    _assert_blocked_by(statuses, 3, 2)
    assert statuses[1]["error"] == "UploadError"
    assert statuses[1]["sha256_agent"] == hashlib.sha256(_APK_BYTES + _PATH.encode()).hexdigest()


def test_an_extractor_error_fails_every_bundle_part_and_uploads_none_of_them(
    tmp_path: Path, device: _Device, uploader: _Uploader, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken(apks: list[tuple[str, Path]], out_dir: Path) -> list[Path]:
        raise ExtractorError("aapt2 badging failed with exit code 1")

    monkeypatch.setattr(acquisition_runner, "extract", broken)
    statuses = _run(tmp_path, uploader)
    assert [(s["part"], s["availability_status"]) for s in statuses] == [
        (1, "acquired"),
        (2, "acquired"),
        *[(n, "failed") for n in range(3, 3 + _BUNDLE)],
    ]
    assert all("aapt2" in s["availability_reason"] for s in statuses[2:])
    assert [s["raw_source"] for s in statuses] == _labels("Stk.apk")
    assert [fields["part"] for fields, _ in uploader.calls] == [1, 2]


def test_a_failing_bundle_upload_marks_only_its_part(
    tmp_path: Path, device: _Device, uploader: _Uploader
) -> None:
    uploader.fail_part = 5
    statuses = _run(tmp_path, uploader)
    assert [s["availability_status"] for s in statuses] == (
        ["acquired"] * 4 + ["failed"] + ["acquired"] * (_BUNDLE - 3)
    )
    assert statuses[4]["part"] == 5 and statuses[4]["raw_source"] == _labels("Stk.apk")[4]


def test_an_existing_apk_evidence_file_is_never_overwritten(
    tmp_path: Path, device: _Device, uploader: _Uploader
) -> None:
    existing = tmp_path / _SESSION / "2-pull_subject_apk-2.bin"
    existing.parent.mkdir(parents=True)
    existing.write_bytes(b"older evidence")
    statuses = _run(tmp_path, uploader)
    assert [s["availability_status"] for s in statuses[:2]] == ["acquired", "failed"]
    _assert_blocked_by(statuses, 3, 2)
    assert existing.read_bytes() == b"older evidence"
    assert not any(call[0] == "pull" for call in device.calls)


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"package_name": "x", "path": "/sdcard/evil.apk"},
        {"path": "/sdcard/evil.apk"},
        {"package_name": "com.x; id"},
        {"package_name": "-h"},
    ],
)
def test_the_job_cannot_carry_an_apk_path_or_a_bad_package_name(
    tmp_path: Path, device: _Device, uploader: _Uploader, parameters: dict[str, str]
) -> None:
    statuses = _run(tmp_path, uploader, parameters=parameters)
    assert [s["availability_status"] for s in statuses] == ["failed"]
    assert device.calls == [] and uploader.calls == []


def test_resolving_the_operation_with_a_path_parameter_is_refused() -> None:
    with pytest.raises(ValueError, match="takes parameters"):
        resolve_operation_parts(
            "pull_subject_apk", {"package_name": "x", "path": "/sdcard/evil.apk"}
        )


def test_the_resolved_parts_keep_agent_side_placeholders_unfilled() -> None:
    parts = resolve_operation_parts("pull_subject_apk", {"package_name": "com.android.stk"})
    assert parts == [
        ("pm path", ["shell", "pm", "path", "com.android.stk"]),
        ("apk file", ["pull", "{apk_path}", "{local_path}"]),
    ]


def test_a_pull_that_exits_zero_but_leaves_no_file_is_not_acquired(
    tmp_path: Path, device: _Device, uploader: _Uploader
) -> None:
    device.writes_file = False
    statuses = _run(tmp_path, uploader)
    assert [(s["part"], s["availability_status"]) for s in statuses[:2]] == [
        (1, "acquired"),
        (2, "unavailable"),
    ]
    _assert_blocked_by(statuses, 3, 2)
    assert [fields["part"] for fields, _ in uploader.calls] == [1]


def test_an_empty_pulled_file_is_not_acquired(
    tmp_path: Path, device: _Device, uploader: _Uploader, monkeypatch: pytest.MonkeyPatch
) -> None:
    def empty_pull(args: list[str], serial: str | None = None, **_: object) -> AdbResult:
        device.calls.append(args)
        if args[0] == "pull":
            Path(args[2]).write_bytes(b"")
            return AdbResult(b"", b"1 file pulled\n", 0)
        return AdbResult(device.pm_output, b"", 0)

    monkeypatch.setattr(acquisition_runner, "run_adb", empty_pull)
    statuses = _run(tmp_path, uploader)
    assert [s["availability_status"] for s in statuses[:2]] == ["acquired", "unavailable"]
    _assert_blocked_by(statuses, 3, 2)


def test_a_path_query_that_is_not_acquired_blocks_the_apk_part_and_the_bundle(
    tmp_path: Path, device: _Device, uploader: _Uploader, monkeypatch: pytest.MonkeyPatch
) -> None:
    def denied(args: list[str], serial: str | None = None, **_: object) -> AdbResult:
        device.calls.append(args)
        return AdbResult(b"", b"Permission denial: not allowed\n", 255)

    monkeypatch.setattr(acquisition_runner, "run_adb", denied)
    statuses = _run(tmp_path, uploader)
    assert [s["part"] for s in statuses] == list(range(1, 3 + _BUNDLE))
    assert statuses[0]["availability_status"] == "denied"
    assert statuses[0]["raw_source"] == "pm path"
    assert statuses[1]["raw_source"] == "apk file"
    assert statuses[1]["availability_reason"] == "prasyarat part 1 tidak diperoleh"
    _assert_blocked_by(statuses, 3, 2)
    assert len(device.calls) == 1  # only the path query ran
    assert uploader.calls == []


# --- timeouts (REF §OPS2: pull 1800 s, other commands 60 s) -----------------------------------


def test_pull_gets_the_long_timeout_and_other_commands_the_short_one() -> None:
    assert adb_commands.timeout_for(["pull", "/a.apk", "/b"]) == 1800
    assert adb_commands.timeout_for(["shell", "pm", "path", "x"]) == 60
    assert adb_commands.timeout_for(["shell", "getprop"]) == 60


def test_run_adb_passes_the_timeout_for_the_command(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[float] = []

    class _Done:
        stdout = b""
        stderr = b""
        returncode = 0

    def fake_run(command: list[str], **kwargs: Any) -> _Done:
        seen.append(kwargs["timeout"])
        assert kwargs["shell"] is False
        return _Done()

    monkeypatch.setattr("src.device.adb_controller.subprocess.run", fake_run)
    run_adb(["pull", "/a.apk", "/b"], "emulator-5554", adb_path="adb")
    run_adb(["shell", "pm", "path", "x"], "emulator-5554", adb_path="adb")
    run_adb(["shell", "pm", "path", "x"], "emulator-5554", adb_path="adb", timeout=5)
    assert seen == [1800, 60, 5]
