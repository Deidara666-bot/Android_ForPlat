"""ADB controller. This card only needs `adb version`; allowlisted operations arrive in v0.30."""

import subprocess

from src.exceptions import AdbError


def adb_version(adb_path: str) -> str:
    """Return the first line of `adb version`. Fixed argument list, never a shell string."""
    try:
        result = subprocess.run(  # noqa: S603
            [adb_path, "version"], capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AdbError(f"cannot run adb at {adb_path!r}: {type(exc).__name__}") from exc
    if result.returncode != 0:
        raise AdbError(f"`adb version` failed with exit code {result.returncode}")
    lines = result.stdout.strip().splitlines()
    if not lines:
        raise AdbError("`adb version` returned no output")
    return lines[0]
