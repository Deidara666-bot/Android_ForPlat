"""Device discovery by polling `adb devices -l`, plus safe (non-evidence) metadata."""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Protocol

from src.device.adb_commands import DEVICE_LIST, SAFE_METADATA_PROPS, safe_prop_args
from src.device.adb_controller import run_adb
from src.device.privilege_detector import detect_privilege
from src.exceptions import AdbError
from src.state.audit_logger import audit


@dataclass(frozen=True)
class DetectedDevice:
    serial: str
    status: str  # "device", "unauthorized", "offline", ...


def parse_devices(output: str) -> list[DetectedDevice]:
    """Parse `adb devices -l` output: `<serial> <status> <key:value ...>` per line."""
    devices: list[DetectedDevice] = []
    in_list = False
    for raw in output.splitlines():
        line = raw.strip()
        if line.startswith("List of devices attached"):
            in_list = True
            continue
        if not in_list or not line or line.startswith("*"):
            continue
        parts = line.split()
        if len(parts) >= 2:
            devices.append(DetectedDevice(serial=parts[0], status=parts[1]))
    return devices


def detect_devices(adb_path: str | None = None) -> list[DetectedDevice]:
    result = run_adb(DEVICE_LIST, adb_path=adb_path)
    if result.returncode != 0:
        raise AdbError(f"`adb devices` failed with exit code {result.returncode}")
    return parse_devices(result.stdout.decode("utf-8", errors="replace"))


def collect_safe_metadata(serial: str, adb_path: str | None = None) -> dict[str, Any]:
    """Read the whitelisted properties plus the privilege state. Not evidence."""
    values: dict[str, str] = {}
    for prop in SAFE_METADATA_PROPS:
        result = run_adb(safe_prop_args(prop), serial, adb_path=adb_path)
        values[prop] = result.stdout.decode("utf-8", errors="replace").strip()
    sdk = values["ro.build.version.sdk"]
    return {
        "manufacturer": values["ro.product.manufacturer"],
        "model": values["ro.product.model"],
        "android_version": values["ro.build.version.release"],
        "api_level": int(sdk) if sdk.isdigit() else None,
        "device_build": values["ro.build.fingerprint"],
        "privilege_state": detect_privilege(serial, adb_path=adb_path).value,
    }


class _Sender(Protocol):
    async def send(self, message: str) -> None: ...


@dataclass
class DeviceMonitor:
    """Polls for devices and reports to the backend whenever the list changes."""

    adb_path: str | None = None
    _cache: dict[str, dict[str, Any]] = field(default_factory=dict)
    _last: tuple[tuple[str, str], ...] | None = None
    connected_count: int = 0

    def reset_reporting(self) -> None:
        """Forget what was last sent (call on every new connection so state is re-sent)."""
        self._last = None

    def snapshot(self) -> list[dict[str, Any]]:
        detected = detect_devices(self.adb_path)
        report: list[dict[str, Any]] = []
        for device in detected:
            entry: dict[str, Any] = {"serial": device.serial, "status": device.status}
            if device.status == "device":
                if device.serial not in self._cache:
                    self._cache[device.serial] = collect_safe_metadata(device.serial, self.adb_path)
                entry.update(self._cache[device.serial])
            else:
                self._cache.pop(device.serial, None)
            report.append(entry)
        self.connected_count = sum(1 for entry in report if entry["status"] == "device")
        return report

    async def poll_and_report(self, websocket: _Sender) -> None:
        try:
            report = await asyncio.to_thread(self.snapshot)
        except AdbError as exc:
            audit("device_poll_failed", str(exc))
            return
        key = tuple(sorted((entry["serial"], entry["status"]) for entry in report))
        if key == self._last:
            return
        await websocket.send(json.dumps({"type": "device_report", "devices": report}))
        audit("device_report_sent", devices=[list(pair) for pair in key])
        self._last = key

    async def run(self, websocket: _Sender, interval_seconds: float) -> None:
        while True:
            await self.poll_and_report(websocket)
            await asyncio.sleep(interval_seconds)
