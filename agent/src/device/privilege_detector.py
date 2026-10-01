"""Reads the privilege state of the shell user. Detection only: it never changes privilege."""

import re

from src.device.adb_commands import PRIVILEGE_PROBE
from src.device.adb_controller import run_adb
from src.exceptions import AdbError
from src.models import PrivilegeState

_UID = re.compile(rb"uid=(\d+)")


def detect_privilege(serial: str | None = None, *, adb_path: str | None = None) -> PrivilegeState:
    try:
        result = run_adb(PRIVILEGE_PROBE, serial, adb_path=adb_path)
    except AdbError:
        return PrivilegeState.unknown
    if result.returncode != 0:
        return PrivilegeState.unknown
    match = _UID.search(result.stdout)
    if match is None:
        return PrivilegeState.unknown
    return PrivilegeState.root_detected if int(match.group(1)) == 0 else PrivilegeState.non_root
