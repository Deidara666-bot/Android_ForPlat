"""The Tier-2 runner against a fake backend (v0.45.8): no adb, no network, no AVD."""

import csv
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

_ROOT = Path(__file__).resolve().parents[3]
_SCRIPT = _ROOT / "scripts" / "experiments" / "tier2_run.py"
_RESET = _ROOT / "scripts" / "adb" / "tier2_reset.sh"
_SERIAL = "emulator-5554"
_SPEC = importlib.util.spec_from_file_location("tier2_run", _SCRIPT)
assert _SPEC is not None and _SPEC.loader is not None
runner = importlib.util.module_from_spec(_SPEC)
sys.modules["tier2_run"] = runner
_SPEC.loader.exec_module(runner)

_LABELS = {
    "pm list packages -U": ("collect_package_inventory", None),
    "dumpsys package": ("collect_package_detail", None),
    "settings secure a11y": ("collect_accessibility_state", None),
    "settings secure nls": ("collect_accessibility_state", None),
    "appops overlay": ("collect_accessibility_state", None),
    "dumpsys usagestats": ("collect_usage_state", None),
    "dumpsys activity": ("collect_usage_state", None),
    "ps": ("collect_usage_state", None),
    "pm path": ("pull_subject_apk", None),
    "apk file": ("pull_subject_apk", None),
}


def _artifact(evidence_id: str, artifact_type: str, value: dict[str, Any], **o: Any) -> dict:
    return {
        "id": f"art-{artifact_type}-{evidence_id}",
        "evidence_id": evidence_id,
        "artifact_type": artifact_type,
        "parser_name": "p",
        "parser_version": "1",
        "subject_key": o.pop("subject_key", None),
        "parsed_value_json": value,
        "parse_status": o.pop("parse_status", "parsed"),
        "provenance": {"acquisition_session_id": "SESSION"},
    }


class FakeApi:
    """Answers like the backend; the scenario is changed through the public attributes."""

    def __init__(self, *, api_level: int = 36, sdk: str = "36", serial: str = _SERIAL) -> None:
        self.api_level = api_level
        self.sdk = sdk
        self.serial = serial
        self.calls: list[tuple[str, str]] = []
        self.status_overrides: dict[str, str] = {}  # raw_source -> availability_status
        self.drop_sources: set[str] = set()  # raw_sources without an evidence row
        self.failed_artifact_sources: set[str] = set()
        self.identity: dict[str, Any] = {
            "first_install_time": "2026-01-01 10:00:00",
            "last_update_time": "2026-01-02 10:00:00",
            "installer_package_name": None,
            "signatures": ["abc"],
        }
        self.sessions: list[dict[str, Any]] = []
        self._artifacts: list[dict[str, Any]] = []

    def get(self, path: str) -> Any:
        self.calls.append(("GET", path))
        if path == "/devices":
            return [
                {
                    "id": "dev-1",
                    "serial": self.serial,
                    "api_level": self.api_level,
                    "connection_state": "connected",
                }
            ]
        if path.startswith("/acquisitions/"):
            return self.sessions[-1]
        if path.endswith("/artifacts"):
            return list(self._artifacts)
        raise AssertionError(path)

    def post(self, path: str, body: dict[str, Any]) -> Any:
        self.calls.append(("POST", path))
        if path == "/cases":
            return {"id": "case-1"}
        assert path == "/acquisitions" and body["profile"] == "tier2_g1"
        assert set(body["parameters"]) == {"package_name"}
        session_id = f"SESSION-{len(self.sessions) + 1}"
        evidence = []
        counter = 0
        for label, (operation, _) in _LABELS.items():
            if label in self.drop_sources:
                continue
            counter += 1
            status = self.status_overrides.get(label, "acquired")
            evidence.append(
                {
                    "id": f"ev-{session_id}-{counter}",
                    "raw_source": label,
                    "operation_id": operation,
                    "availability_status": status,
                    "availability_reason": None if status == "acquired" else "uji",
                    "acquired_at": "2026-10-03T12:00:00Z",
                    "privilege_state": "non_root",
                }
            )
        self.sessions.append(
            {
                "id": session_id,
                "status": "completed",
                "android_version": "16",
                "api_level": self.api_level,
                "device_build": "BUILD",
                "evidence": evidence,
            }
        )
        by_label = {e["raw_source"]: e["id"] for e in evidence}
        self._add_artifacts(session_id, by_label, body["parameters"]["package_name"])
        return {"id": session_id}

    def _add_artifacts(self, session_id: str, ids: dict[str, str], subject: str) -> None:
        def add(label: str, artifact_type: str, value: dict[str, Any], **o: Any) -> None:
            if label not in ids:
                return
            status = "failed" if label in self.failed_artifact_sources else "parsed"
            row = _artifact(ids[label], artifact_type, value, parse_status=status, **o)
            row["provenance"]["acquisition_session_id"] = session_id
            self._artifacts.append(row)

        add("pm list packages -U", "package_inventory_entry", {"uid": 1000}, subject_key="android")
        add(
            "dumpsys package",
            "package_identity",
            {"user_id": 10001, **self.identity},
            subject_key=subject,
        )
        add(
            "dumpsys package",
            "component_declared",
            {"name": "x/.R", "kind": "receiver"},
            subject_key=subject,
        )
        add("dumpsys package", "requested_permission", {"name": "p"}, subject_key=subject)
        add(
            "dumpsys package",
            "granted_permission",
            {"name": "p", "granted": True},
            subject_key=subject,
        )
        add("settings secure a11y", "settings_secure_list", {"count": 0}, subject_key=None)
        add("settings secure nls", "settings_secure_list", {"count": 0}, subject_key=None)
        add("appops overlay", "overlay_app_op", {"mode": "default"}, subject_key=subject)
        add("dumpsys usagestats", "usage_event", {"event": "ACTIVITY_RESUMED"}, subject_key=subject)
        add(
            "dumpsys activity",
            "resumed_activity",
            {"has_resumed_activity": True},
            subject_key=subject,
        )
        add("ps", "running_process", {"pid": 1}, subject_key=subject)
        # device metadata lives in another operation's evidence in reality; the guard reads it here
        meta = _artifact(
            "ev-meta",
            "device_build_property",
            {"key": "ro.build.version.sdk", "value": self.sdk},
            subject_key="ro.build.version.sdk",
        )
        meta["provenance"]["acquisition_session_id"] = session_id
        self._artifacts.append(meta)


class Recorder:
    def __init__(self) -> None:
        self.resets: list[tuple[str, str]] = []

    def reset(self, env: str, serial: str) -> None:
        self.resets.append((env, serial))


def _run(
    tmp_path: Path, api: FakeApi, recorder: Recorder, *extra: str, env: str = "avd1-api36"
) -> tuple[int, Path]:
    output = tmp_path / "out.csv"
    hooks = runner.Hooks(
        reset=recorder.reset,
        sleep=lambda _seconds: None,
        git_commit="abc123",
        adb_version="Android Debug Bridge version 1.0.41",
        command_table=runner.load_command_table(),
    )
    code = runner.main(
        ["--env", env, "--profile", "tier2_g1", "--output", str(output), *extra],
        api=api,
        hooks=hooks,
    )
    return code, output


def _rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_the_csv_has_one_row_per_artifact_per_subject_per_repetition(tmp_path: Path) -> None:
    api, recorder = FakeApi(), Recorder()
    code, output = _run(tmp_path, api, recorder, "--reps", "2")
    assert code == 0
    with output.open(newline="", encoding="utf-8") as handle:
        assert tuple(csv.reader(handle).__next__()) == runner.COLUMNS
    rows = _rows(output)
    assert len(rows) == 16 * 2 * 2
    assert {(r["subject"], r["rep"]) for r in rows} == {
        (s, str(n)) for s in ("com.android.settings", "com.android.stk") for n in (1, 2)
    }
    assert [r["artifact_id"] for r in rows[:16]] == [t.artifact_id for t in runner.TIER1]
    assert recorder.resets == [("avd1-api36", _SERIAL)] * 4  # a reset before every session
    first = rows[0]
    assert (first["env"], first["api"], first["android_version"], first["build"]) == (
        "avd1-api36",
        "36",
        "16",
        "BUILD",
    )
    assert first["git_commit"] == "abc123" and first["adb_version"].startswith("Android Debug")
    assert first["device_or_emulator"] == _SERIAL and first["privilege_state"] == "non_root"
    assert first["command"] == f"adb -s {_SERIAL} shell pm list packages -U"
    by_id = {r["artifact_id"]: r for r in rows[:16]}
    assert by_id["G1-A7"]["command"].endswith("shell dumpsys package com.android.settings")
    assert by_id["G1-A3"]["command"].startswith(f"adb -s {_SERIAL} pull {{apk_path}}")
    assert "pm path com.android.settings" in by_id["G1-A2"]["command"]
    assert " ; " in by_id["G1-A11"]["command"]  # two parts, two commands


def test_a_part_that_is_not_acquired_is_reported_with_the_status_the_backend_recorded(
    tmp_path: Path,
) -> None:
    api = FakeApi()
    api.status_overrides = {"settings secure nls": "denied"}
    api.drop_sources = {"ps"}
    code, output = _run(tmp_path, api, Recorder(), "--reps", "1", "--subject", "com.android.stk")
    assert code == 0
    by_id = {r["artifact_id"]: r for r in _rows(output)}
    assert (by_id["G1-B2"]["availability_status"], by_id["G1-B2"]["actual_result"]) == (
        "denied",
        "denied",
    )
    assert by_id["G1-B2"]["availability_reason"] == "uji"
    assert by_id["G1-B1"]["actual_result"] == "observed"
    # one of the two parts of G1-A11 has no evidence row at all: not acquired, never "false"
    assert by_id["G1-A11"]["availability_status"] == "not_acquired"
    assert by_id["G1-A11"]["actual_result"] == "not_acquired"
    assert by_id["G1-A10"]["availability_status"] == "acquired"


def test_acquired_but_empty_or_unparsed_is_told_apart(tmp_path: Path) -> None:
    api = FakeApi()
    api.failed_artifact_sources = {"dumpsys usagestats"}
    api.identity = {**api.identity, "signatures": []}
    code, output = _run(tmp_path, api, Recorder(), "--reps", "1", "--subject", "com.android.stk")
    assert code == 0
    by_id = {r["artifact_id"]: r for r in _rows(output)}
    assert by_id["G1-A10"]["actual_result"] == "parse_incomplete"
    assert by_id["G1-A10"]["availability_status"] == "acquired"
    assert by_id["G1-A5"]["actual_result"] == "not_observed"  # installer is null
    assert by_id["G1-A6"]["actual_result"] == "not_observed"  # no signatures
    assert by_id["G1-A4"]["actual_result"] == "observed"


def test_an_unknown_environment_stops_before_the_api_and_any_reset(tmp_path: Path) -> None:
    api, recorder = FakeApi(), Recorder()
    code, output = _run(tmp_path, api, recorder, env="pixel-9")
    assert code == 2
    assert recorder.resets == [] and api.calls == [] and not output.exists()


def test_a_label_with_no_device_stops_before_the_first_reset_and_writes_no_file(
    tmp_path: Path,
) -> None:
    api, recorder = FakeApi(), Recorder()  # only an emulator is connected
    code, output = _run(tmp_path, api, recorder, env="a10-api99")
    assert code == 2
    assert recorder.resets == [] and not output.exists()
    assert ("POST", "/cases") not in api.calls


def test_a_device_whose_api_differs_from_the_label_stops_before_the_first_reset(
    tmp_path: Path,
) -> None:
    api, recorder = FakeApi(api_level=35), Recorder()
    code, output = _run(tmp_path, api, recorder)
    assert code == 2 and recorder.resets == [] and not output.exists()


def test_metadata_sdk_that_differs_from_the_label_is_not_recorded(tmp_path: Path) -> None:
    api, recorder = FakeApi(sdk="35"), Recorder()  # the device list says 36, the evidence says 35
    code, output = _run(tmp_path, api, recorder, "--reps", "3")
    assert code == 2
    assert len(recorder.resets) == 1 and not output.exists()  # stopped after the first session


def test_an_existing_csv_is_never_overwritten(tmp_path: Path) -> None:
    output = tmp_path / "out.csv"
    output.write_text("keep me", encoding="utf-8")
    api, recorder = FakeApi(), Recorder()
    code, _ = _run(tmp_path, api, recorder)
    assert code == 2 and output.read_text(encoding="utf-8") == "keep me"
    assert recorder.resets == [] and api.calls == []


@pytest.mark.parametrize("profile", ["tier2_g2g3", "tier2_confirm", "nope"])
def test_profiles_that_are_not_available_yet_stop_the_run(tmp_path: Path, profile: str) -> None:
    api, recorder = FakeApi(), Recorder()
    output = tmp_path / "out.csv"
    code = runner.main(
        ["--env", "avd1-api36", "--profile", profile, "--output", str(output)],
        api=api,
        hooks=runner.Hooks(reset=recorder.reset, sleep=lambda _s: None, command_table={}),
    )
    assert code == 2 and recorder.resets == [] and not output.exists()


def test_the_command_text_comes_from_the_agent_table() -> None:
    table = runner.load_command_table()
    assert table["pm list packages -U"] == ["shell", "pm", "list", "packages", "-U"]
    assert "dumpsys package" in table and "appops overlay" in table
    assert "static:manifest.txt" not in table  # bundle parts have no adb command


@pytest.mark.parametrize("label", ["", "bogus", "avd1-api3", "a10", "avd1-api36; reboot"])
def test_the_reset_script_refuses_an_unknown_environment_before_touching_adb(label: str) -> None:
    try:
        bash = runner.find_bash()
    except runner.RunnerStop:
        pytest.skip("needs bash")
    result = subprocess.run(
        [bash, str(_RESET), label],
        capture_output=True,
        text=True,
        env={**os.environ, "ADB": "/nonexistent/adb"},
        check=False,
    )
    assert result.returncode == 2
    assert "unknown environment" in result.stderr
