"""Availability status of one acquisition result (01_BREAKDOWN §8).

Classification order is binding: unsupported -> denied -> unavailable -> failed (the rest).
A status other than `acquired` is a fact about the evidence, never a negative finding.
"""

import re

from src.device.adb_controller import AdbResult
from src.models import AvailabilityStatus

REASON_MAX_CHARS = 200


# `: not found` / `inaccessible or not found` come from the device shell; a bare "not found"
# would also match adb's own `error: device 'x' not found`, which is a transport failure.
_UNSUPPORTED = re.compile(
    r"(inaccessible or not found|: not found|unknown command|can't find service)", re.IGNORECASE
)
_DENIED = re.compile(r"(permission denial|securityexception|permission denied)", re.IGNORECASE)


def _snippet(text: str) -> str:
    return " ".join(text.split())[:REASON_MAX_CHARS]


def is_acquired(result: AdbResult) -> bool:
    """A command that succeeded and produced output."""
    return result.returncode == 0 and bool(result.stdout)


def classify_failure(result: AdbResult) -> tuple[AvailabilityStatus, str]:
    """Status and reason for a result that is not a usable acquisition.

    Raises ValueError for a successful result: nothing to classify, and silently returning
    a failure status for good evidence would be wrong.
    """
    if is_acquired(result):
        raise ValueError("result is a successful acquisition, not a failure")

    stderr = result.stderr.decode("utf-8", errors="replace")
    # With a non-zero exit, older devices report errors on stdout; a zero exit never does.
    text = stderr if result.returncode == 0 else stderr + result.stdout.decode("utf-8", "replace")
    reason = _snippet(stderr)  # stderr only: stdout can hold evidence content

    if _UNSUPPORTED.search(text):
        return AvailabilityStatus.unsupported, reason or "command or service is not supported"
    if _DENIED.search(text):
        return AvailabilityStatus.denied, reason or "permission denied"
    if result.returncode == 0:
        return AvailabilityStatus.unavailable, reason or "command succeeded with empty output"
    return AvailabilityStatus.failed, reason or f"adb exited with code {result.returncode}"
