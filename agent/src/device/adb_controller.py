"""ADB controller. The single place that spawns `adb`, always with an argument list."""

import subprocess
from dataclasses import dataclass

from src.config import get_settings
from src.device.adb_commands import VERSION
from src.exceptions import AdbError


@dataclass(frozen=True)
class AdbResult:
    stdout: bytes
    stderr: bytes
    returncode: int


def run_adb(
    args: list[str], serial: str | None = None, *, adb_path: str | None = None
) -> AdbResult:
    """Run `adb [-s serial] *args` without a shell. Output stays as raw bytes."""
    command = [adb_path or get_settings().adb_path]
    if serial is not None:
        command += ["-s", serial]
    command += args
    try:
        completed = subprocess.run(  # noqa: S603
            command, shell=False, capture_output=True, timeout=60, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdbError(f"cannot run adb: {type(exc).__name__}") from exc
    return AdbResult(completed.stdout, completed.stderr, completed.returncode)


def adb_version(adb_path: str) -> str:
    """Return the first line of `adb version`."""
    result = run_adb(VERSION, adb_path=adb_path)
    if result.returncode != 0:
        raise AdbError(f"`adb version` failed with exit code {result.returncode}")
    lines = result.stdout.decode("utf-8", errors="replace").strip().splitlines()
    if not lines:
        raise AdbError("`adb version` returned no output")
    return lines[0]
