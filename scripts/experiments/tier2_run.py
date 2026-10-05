#!/usr/bin/env python3
"""Tier-2 runner: reset the environment, acquire through the agent, record one CSV row per
Tier-1 artifact per subject per repetition (REF §TIER2, 01_BREAKDOWN §11.1).

    python scripts/experiments/tier2_run.py --env avd1-api36 --profile tier2_g1 --reps 3

The runner is a host-side script. It talks to the backend API like an examiner would (JWT) and
resets the environment with `scripts/adb/tier2_reset.sh`; neither the backend nor the agent
resets anything. The CSV is written once, at the end: a run that stops writes no file, so a
partial run can never be mistaken for a result. Standard library only.

Nothing is guessed: a part without an evidence row is `not_acquired`, any other state is
reported as the backend recorded it, and a wrong environment label stops the run before the
first reset.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "experiments" / "feasibility_tier2" / "results"
RESET_SCRIPT = ROOT / "scripts" / "adb" / "tier2_reset.sh"

COLUMNS = (
    "artifact_id",
    "env",
    "subject",
    "rep",
    "android_version",
    "api",
    "build",
    "device_or_emulator",
    "operation_id",
    "command",
    "privilege_state",
    "test_action",
    "expected_evidence",
    "actual_result",
    "availability_status",
    "availability_reason",
    "raw_output_ref",
    "temporal_semantics",
    "git_commit",
    "adb_version",
    "acquired_at",
)

ENV_PATTERN = re.compile(r"^(?P<kind>avd1|avd2|a10)-api(?P<api>\d{2})$")
DEFAULT_SUBJECTS = ("com.android.settings", "com.android.stk")
# Profiles the runner can drive today; `tier2_g2g3` and `tier2_confirm` need operations that
# are not mapped yet (v0.70, v0.90).
SUPPORTED_PROFILES = ("tier2_g1",)
KNOWN_PROFILES = ("tier2_g1", "tier2_g2g3", "tier2_confirm")
NOT_ACQUIRED = "not_acquired"
# Tier-2 cannot judge this artifact yet (REF §TIER2): reported apart, never counted in 3/3-0/3.
NOT_EVALUATED = "not_evaluated"
SDK_PROPERTY = "ro.build.version.sdk"
DEFAULT_SESSION_TIMEOUT = 900
SETTLE_SECONDS = 5

_STATIC_COMMAND = "static extractor (aapt2, apksigner) on the pulled APK; no adb command"


class RunnerStop(Exception):
    """The run cannot continue; nothing is written."""


@dataclass(frozen=True)
class Tier1:
    artifact_id: str
    name: str
    operation_id: str
    # `raw_source` labels of the parts that carry the artifact; `<label>:*` = every part whose
    # label is `<label>` or starts with `<label>:` (one part per APK file for `apk file`)
    sources: tuple[str, ...]
    temporal: str  # 01_BREAKDOWN §9.1 "temporal semantics" column
    action: str
    check: str  # key of the content check below


_PKG = "dumpsys package"
_USAGE = "dumpsys usagestats"
_ACCESS = "collect_accessibility_state"
TIER1: tuple[Tier1, ...] = (
    Tier1("G1-A1", "package name, UID, version", "collect_package_inventory",
          ("pm list packages -U",), "current", "list installed packages with UIDs", "inventory"),
    Tier1("G1-A2", "APK path", "pull_subject_apk", ("pm path",), "current",
          "ask the device for the subject's APK path", "acquired"),
    Tier1("G1-A3", "APK file + SHA-256", "pull_subject_apk", ("apk file:*",), "current",
          "pull every APK file the device reported", "acquired"),
    Tier1("G1-A4", "firstInstallTime / lastUpdateTime", "collect_package_detail", (_PKG,),
          "historical metadata", "read the subject's package record", "install_times"),
    Tier1("G1-A5", "installer / initiating / originating info", "collect_package_detail",
          (_PKG,), "current metadata", "read the subject's package record", "installer"),
    Tier1("G1-A6", "signing / certificate", "collect_package_detail", (_PKG,), "current",
          "read the subject's package record", "signatures"),
    Tier1("G1-A7", "declared components", "collect_package_detail", (_PKG,), "current",
          "read the subject's package record", "components"),
    Tier1("G1-A8", "requested permissions", "collect_package_detail", (_PKG,), "current",
          "read the subject's package record", "requested"),
    Tier1("G1-A9", "granted permission state", "collect_package_detail", (_PKG,), "current",
          "read the subject's package record", "granted"),
    Tier1("G1-A10", "UsageStats / UsageEvents", "collect_usage_state", (_USAGE,),
          "historical limited", "read the last 24 hours of usage events", "usage_events"),
    Tier1("G1-A11", "process / activity state", "collect_usage_state",
          ("dumpsys activity", "ps"), "current", "read the resumed activity and the process table",
          "process_activity"),
    Tier1("G1-B1", "enabled Accessibility Service", _ACCESS, ("settings secure a11y",),
          "current", "read the enabled accessibility services setting", "secure_list"),
    Tier1("G1-B2", "enabled notification listener", _ACCESS, ("settings secure nls",),
          "current", "read the enabled notification listeners setting", "secure_list"),
    Tier1("G1-B3", "overlay / AppOps state", _ACCESS, ("appops overlay",), "current",
          "read the overlay app-op of the subject", "overlay"),
    Tier1("G1-B7", "receiver / service persistence declaration", "collect_package_detail",
          (_PKG,), "current", "read the subject's package record", "receivers"),
    Tier1("G1-B8", "observed boot / package-event execution", "collect_usage_state", (_USAGE,),
          "historical limited",
          "read usage events (source availability is G1-A10; boot or package-event attribution "
          "is not evaluated until v0.80)", NOT_EVALUATED),
)


# --- environment label -------------------------------------------------------------------------


def parse_env(label: str) -> tuple[str, int]:
    """(kind, api) of a label such as `avd1-api36`; anything else stops the run."""
    match = ENV_PATTERN.fullmatch(label)
    if match is None:
        raise RunnerStop(f"unknown environment {label!r}; nothing was reset")
    return match["kind"], int(match["api"])


def pick_device(devices: Sequence[dict[str, Any]], kind: str, api: int, serial: str | None) -> dict:
    """The one connected device that belongs to the label, or a stop."""
    wanted_emulator = kind != "a10"
    found = [
        d
        for d in devices
        if d["connection_state"] == "connected"
        and str(d["serial"]).startswith("emulator-") == wanted_emulator
        and (serial is None or d["serial"] == serial)
    ]
    if not found:
        raise RunnerStop(f"no connected device matches the environment {kind}-api{api}")
    if len(found) > 1:
        raise RunnerStop("more than one matching device is connected; pass --serial")
    device = found[0]
    if device["api_level"] != api:
        raise RunnerStop(
            f"the label says api{api} but the connected device reports api{device['api_level']}"
        )
    return device


# --- backend API -------------------------------------------------------------------------------


class ApiLike(Protocol):
    def get(self, path: str) -> Any: ...
    def post(self, path: str, body: dict[str, Any]) -> Any: ...


class Api:
    def __init__(self, base: str, token: str) -> None:
        self._base = base.rstrip("/")
        self._headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _call(self, method: str, path: str, body: dict[str, Any] | None) -> Any:
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(
            self._base + path, data=data, headers=self._headers, method=method
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            detail = error.read().decode(errors="replace")[:300]
            raise RunnerStop(f"{method} {path} -> HTTP {error.code}: {detail}") from None
        except urllib.error.URLError as error:
            raise RunnerStop(f"{method} {path}: backend not reachable ({error.reason})") from None

    def get(self, path: str) -> Any:
        return self._call("GET", path, None)

    def post(self, path: str, body: dict[str, Any]) -> Any:
        return self._call("POST", path, body)


def examiner_token(email: str) -> str:
    """JWT from `FORPLAT_JWT`, else from the backend's development helper (never printed)."""
    token = os.environ.get("FORPLAT_JWT")
    if token:
        return token
    backend = ROOT / "backend"
    python = next(
        (p for p in (backend / ".venv/Scripts/python.exe", backend / ".venv/bin/python") if p.exists()),
        None,
    )
    if python is None:
        raise RunnerStop("no JWT: set FORPLAT_JWT or create backend/.venv")
    result = subprocess.run(
        [str(python), "-m", "app.cli.dev_token", "--email", email],
        cwd=backend,
        capture_output=True,
        text=True,
        check=False,
    )
    lines = result.stdout.strip().splitlines()
    if result.returncode != 0 or not lines:
        raise RunnerStop("could not obtain a JWT for the examiner account")
    return lines[-1]


# --- command text (from the agent's own table, so the strings live in one place) --------------


def load_command_table() -> dict[str, list[str]]:
    """`raw_source` label -> adb argument list, read from `agent/src/device/adb_commands.py`."""
    path = ROOT / "agent" / "src" / "device" / "adb_commands.py"
    spec = importlib.util.spec_from_file_location("forplat_adb_commands", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    table: dict[str, list[str]] = {}
    for operation, args in module.OPERATION_ARGS.items():
        table[module.RAW_SOURCE_LABEL[operation]] = list(args)
    for parts in module.OPERATION_PARTS.values():
        for label, args in parts:
            table[label] = list(args)
    return table


def _quote(arg: str) -> str:
    """Shell quoting for display; `{placeholder}` braces stay readable."""
    return arg if re.fullmatch(r"[\w@%+=:,./{}-]+", arg) else shlex.quote(arg)


def command_text(
    sources: Iterable[str], table: dict[str, list[str]], serial: str, subject: str
) -> str:
    texts = []
    for label in sources:
        args = table.get(label.removesuffix(":*"))
        if args is None:
            texts.append(_STATIC_COMMAND)
            continue
        filled = [subject if arg == "{package_name}" else arg for arg in args]
        texts.append(" ".join(_quote(arg) for arg in ["adb", "-s", serial, *filled]))
    return " ; ".join(texts)


# --- reading one finished session ----------------------------------------------------------------


@dataclass(frozen=True)
class PartResult:
    status: str
    reason: str | None
    evidence_ids: tuple[str, ...]
    acquired_at: str | None
    privilege_state: str | None
    parse_complete: bool
    artifacts: tuple[dict[str, Any], ...]


def expand_source(evidence: Sequence[dict[str, Any]], source: str) -> list[str]:
    """The part labels a source stands for: itself, or for `<label>:*` every label present in
    the session's evidence (all APK parts); none present -> the bare label (not acquired)."""
    if not source.endswith(":*"):
        return [source]
    base = source[:-2]
    found = sorted(
        {
            e["raw_source"]
            for e in evidence
            if e["raw_source"] == base or e["raw_source"].startswith(base + ":")
        }
    )
    return found or [base]


def part_result(
    evidence: Sequence[dict[str, Any]], artifacts: Sequence[dict[str, Any]], label: str
) -> PartResult:
    rows = [e for e in evidence if e["raw_source"] == label]
    if not rows:
        return PartResult(NOT_ACQUIRED, "no evidence row for this part", (), None, None, False, ())
    acquired = [e for e in rows if e["availability_status"] == "acquired"]
    if not acquired:
        last = rows[-1]
        return PartResult(
            last["availability_status"],
            last.get("availability_reason"),
            tuple(e["id"] for e in rows),
            last["acquired_at"],
            last.get("privilege_state"),
            False,
            (),
        )
    ids = {e["id"] for e in acquired}
    own = tuple(a for a in artifacts if a["evidence_id"] in ids)
    newest = max((a["parser_version"] for a in own), key=_version_key, default=None)
    current = tuple(a for a in own if a["parser_version"] == newest)
    # `pm path` and `apk file` have no parser: acquired is all there is to say about them.
    parse_complete = (
        all(a["parse_status"] in ("parsed", "empty") for a in current) if current else True
    )
    return PartResult(
        "acquired",
        None,
        tuple(sorted(ids)),
        max(e["acquired_at"] for e in acquired),
        next((e["privilege_state"] for e in acquired if e.get("privilege_state")), None),
        parse_complete,
        current,
    )


def _version_key(version: str) -> tuple[int, str]:
    return (int(version), version) if version.isdigit() else (-1, version)


def _parsed(artifacts: Iterable[dict[str, Any]], artifact_type: str) -> list[dict[str, Any]]:
    return [
        a for a in artifacts if a["artifact_type"] == artifact_type and a["parse_status"] == "parsed"
    ]


def _values(artifacts: Iterable[dict[str, Any]], artifact_type: str) -> list[dict[str, Any]]:
    return [a["parsed_value_json"] for a in _parsed(artifacts, artifact_type)]


def _identity(artifacts: Sequence[dict[str, Any]]) -> dict[str, Any]:
    identities = _values(artifacts, "package_identity")
    return identities[0] if identities else {}


# Content checks: is the datum the Tier-1 artifact stands for actually present in the output?
CHECKS: dict[str, Callable[[Sequence[dict[str, Any]]], bool]] = {
    "acquired": lambda artifacts: True,
    "inventory": lambda a: bool(_parsed(a, "package_inventory_entry")),
    "install_times": lambda a: bool(
        _identity(a).get("first_install_time") and _identity(a).get("last_update_time")
    ),
    "installer": lambda a: bool(_identity(a).get("installer_package_name")),
    "signatures": lambda a: bool(_identity(a).get("signatures")),
    "components": lambda a: bool(_parsed(a, "component_declared")),
    "requested": lambda a: bool(_parsed(a, "requested_permission")),
    "granted": lambda a: bool(_parsed(a, "granted_permission")),
    "receivers": lambda a: any(
        v.get("kind") in ("receiver", "service") for v in _values(a, "component_declared")
    ),
    "usage_events": lambda a: bool(_parsed(a, "usage_event")),
    "process_activity": lambda a: bool(_parsed(a, "running_process"))
    or any(v.get("has_resumed_activity") is True for v in _values(a, "resumed_activity")),
    "secure_list": lambda a: bool(_parsed(a, "settings_secure_list")),
    "overlay": lambda a: bool(_parsed(a, "overlay_app_op")),
}


def artifact_row(
    tier1: Tier1,
    evidence: Sequence[dict[str, Any]],
    artifacts: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Status, reason and a content verdict for one Tier-1 artifact of one session."""
    parts = [
        part_result(evidence, artifacts, label)
        for source in tier1.sources
        for label in expand_source(evidence, source)
    ]
    broken = next((p for p in parts if p.status != "acquired"), None)
    if broken is not None:
        status, reason, actual = broken.status, broken.reason, broken.status
    else:
        status, reason = "acquired", None
        if not all(p.parse_complete for p in parts):
            actual = "parse_incomplete"
        else:
            merged = [a for p in parts for a in p.artifacts]
            judged = tier1.check != NOT_EVALUATED and CHECKS[tier1.check](merged)
            actual = "observed" if judged else "not_observed"
    if tier1.check == NOT_EVALUATED:
        actual = NOT_EVALUATED  # whatever the source returned, there is nothing to judge it by
    times = [p.acquired_at for p in parts if p.acquired_at]
    return {
        "availability_status": status,
        "availability_reason": reason or "",
        "actual_result": actual,
        "raw_output_ref": ";".join(i for p in parts for i in p.evidence_ids),
        "privilege_state": next((p.privilege_state for p in parts if p.privilege_state), "") or "",
        "acquired_at": max(times) if times else "",
    }


# --- the run -------------------------------------------------------------------------------------


@dataclass
class Hooks:
    """Everything with side effects outside the API, replaceable in tests."""

    reset: Callable[[str, str], None]
    sleep: Callable[[float], None] = time.sleep
    git_commit: str = "unknown"
    adb_version: str = "unknown"
    command_table: dict[str, list[str]] | None = None


def find_bash() -> str:
    """A real bash. On Windows the `bash` the loader finds first can be the WSL launcher, so
    `FORPLAT_BASH` wins, then a `bash` on PATH outside System32, then the usual Git for Windows."""
    override = os.environ.get("FORPLAT_BASH")
    if override:
        return override
    found = shutil.which("bash")
    if found and "system32" not in found.lower():
        return found
    for variable in ("ProgramFiles", "ProgramW6432", "LOCALAPPDATA"):
        base = os.environ.get(variable)
        for tail in ("Git/bin/bash.exe", "Programs/Git/bin/bash.exe"):
            candidate = Path(base, tail) if base else None
            if candidate is not None and candidate.exists():
                return str(candidate)
    if found:
        return found
    raise RunnerStop("bash not found: install Git for Windows or set FORPLAT_BASH")


def run_reset(env: str, serial: str) -> None:
    result = subprocess.run(
        [find_bash(), str(RESET_SCRIPT), env, serial], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RunnerStop(f"reset failed ({result.returncode}): {result.stderr.strip()[:300]}")


def _wait_connected(api: ApiLike, serial: str, hooks: Hooks, attempts: int = 60) -> None:
    for _ in range(attempts):
        for device in api.get("/devices"):
            if device["serial"] == serial and device["connection_state"] == "connected":
                return
        hooks.sleep(2)
    raise RunnerStop(f"{serial} did not come back as connected after the reset")


def _wait_session(api: ApiLike, session_id: str, hooks: Hooks, timeout: int) -> dict[str, Any]:
    waited = 0.0
    while True:
        detail = api.get(f"/acquisitions/{session_id}")
        if detail["status"] != "running":
            return detail
        if waited >= timeout:
            raise RunnerStop(f"session {session_id} still running after {timeout}s")
        hooks.sleep(2)
        waited += 2


def _session_sdk(artifacts: Sequence[dict[str, Any]]) -> str | None:
    for artifact in artifacts:
        if (
            artifact["artifact_type"] == "device_build_property"
            and artifact["subject_key"] == SDK_PROPERTY
            and artifact["parse_status"] == "parsed"
        ):
            return str(artifact["parsed_value_json"].get("value", "")).strip() or None
    return None


def run_tier2(
    args: argparse.Namespace, api: ApiLike, hooks: Hooks
) -> list[dict[str, Any]]:
    kind, label_api = parse_env(args.env)
    if args.profile not in KNOWN_PROFILES:
        raise RunnerStop(f"unknown profile {args.profile!r}")
    if args.profile not in SUPPORTED_PROFILES:
        raise RunnerStop(f"profile {args.profile!r} needs operations that are not mapped yet")
    if args.reps < 1:
        raise RunnerStop("--reps must be at least 1")
    device = pick_device(api.get("/devices"), kind, label_api, args.serial)
    serial = device["serial"]
    table = hooks.command_table if hooks.command_table is not None else load_command_table()

    case = api.post("/cases", {"case_number": args.case_number, "title": f"Tier-2 {args.profile} {args.env}"})
    rows: list[dict[str, Any]] = []
    guard_done = False
    for rep in range(1, args.reps + 1):
        for subject in args.subject:
            hooks.reset(args.env, serial)
            hooks.sleep(SETTLE_SECONDS)
            _wait_connected(api, serial, hooks)
            started = api.post(
                "/acquisitions",
                {
                    "case_id": case["id"],
                    "device_id": device["id"],
                    "profile": args.profile,
                    "parameters": {"package_name": subject},
                },
            )
            detail = _wait_session(api, started["id"], hooks, args.session_timeout)
            all_artifacts = api.get(f"/cases/{case['id']}/artifacts")
            artifacts = [
                a
                for a in all_artifacts
                if a["provenance"]["acquisition_session_id"] == detail["id"]
            ]
            if not guard_done:
                sdk = _session_sdk(artifacts)
                if sdk != str(label_api):
                    raise RunnerStop(
                        f"the label says api{label_api} but collect_device_metadata reports "
                        f"sdk {sdk!r}; nothing was written"
                    )
                guard_done = True
            evidence = detail["evidence"]
            for tier1 in TIER1:
                result = artifact_row(tier1, evidence, artifacts)
                rows.append(
                    {
                        "artifact_id": tier1.artifact_id,
                        "env": args.env,
                        "subject": subject,
                        "rep": rep,
                        "android_version": detail["android_version"],
                        "api": detail["api_level"],
                        "build": detail["device_build"],
                        "device_or_emulator": serial,
                        "operation_id": tier1.operation_id,
                        "command": command_text(tier1.sources, table, serial, subject),
                        "privilege_state": result["privilege_state"],
                        "test_action": f"{tier1.action} (profile {args.profile}, after reset)",
                        "expected_evidence": tier1.name,
                        "actual_result": result["actual_result"],
                        "availability_status": result["availability_status"],
                        "availability_reason": result["availability_reason"],
                        "raw_output_ref": result["raw_output_ref"],
                        "temporal_semantics": tier1.temporal,
                        "git_commit": hooks.git_commit,
                        "adb_version": hooks.adb_version,
                        "acquired_at": result["acquired_at"],
                    }
                )
    return rows


def write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    """Written to a temporary file first, so an interrupted write leaves no result."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def _capture(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False, cwd=ROOT)
    except OSError:
        return "unknown"
    return result.stdout.strip().replace("\n", " ") if result.returncode == 0 else "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--env", required=True, help="avd1-api36 | avd2-api<N> | a10-api<N>")
    parser.add_argument("--profile", required=True, help="tier2_g1 (others: not mapped yet)")
    parser.add_argument("--reps", type=int, default=3)
    parser.add_argument("--subject", action="append", help="package; repeat for several")
    parser.add_argument("--serial", help="adb serial when several devices match")
    parser.add_argument("--api-base", default="http://localhost:8000/api")
    parser.add_argument("--email", default="pemeriksa@lab.local", help="examiner account")
    parser.add_argument("--case-number", help="default: TIER2-<profile>-<env>-<UTC time>")
    parser.add_argument("--output", type=Path, help="default: experiments/feasibility_tier2/results")
    parser.add_argument("--session-timeout", type=int, default=DEFAULT_SESSION_TIMEOUT)
    return parser


def main(
    argv: Sequence[str] | None = None,
    *,
    api: ApiLike | None = None,
    hooks: Hooks | None = None,
) -> int:
    args = build_parser().parse_args(argv)
    args.subject = args.subject or list(DEFAULT_SUBJECTS)
    stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    args.case_number = args.case_number or f"TIER2-{args.profile}-{args.env}-{stamp}".upper()
    output = args.output or RESULTS_DIR / f"{args.profile}_{args.env}.csv"
    try:
        parse_env(args.env)  # first thing: a wrong label touches nothing, not even the API
        if output.exists():
            raise RunnerStop(f"{output} already exists; it is never overwritten")
        client = api or Api(args.api_base, examiner_token(args.email))
        active = hooks or Hooks(
            reset=run_reset,
            git_commit=_capture(["git", "rev-parse", "HEAD"]),
            adb_version=_capture(["adb", "version"]),
        )
        rows = run_tier2(args, client, active)
        write_csv(output, rows)
    except RunnerStop as stop:
        print(f"tier2_run: stopped: {stop}", file=sys.stderr)
        return 2
    print(f"tier2_run: {len(rows)} rows -> {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
