import json
from pathlib import Path

import pytest

from src.device import device_detection
from src.device.adb_commands import SAFE_METADATA_PROPS, safe_prop_args
from src.device.adb_controller import AdbResult
from src.device.device_detection import DetectedDevice, DeviceMonitor, parse_devices

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _fixture(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


def test_zero_devices() -> None:
    assert parse_devices(_fixture("adb_devices_0.txt")) == []


def test_one_device() -> None:
    assert parse_devices(_fixture("adb_devices_1.txt")) == [
        DetectedDevice("emulator-5554", "device")
    ]


def test_unauthorized_and_offline_are_reported_with_status() -> None:
    assert parse_devices(_fixture("adb_devices_unauthorized.txt")) == [
        DetectedDevice("R58M123ABC", "unauthorized"),
        DetectedDevice("emulator-5554", "offline"),
    ]


def test_only_whitelisted_properties_can_be_read() -> None:
    assert safe_prop_args("ro.build.version.sdk") == ["shell", "getprop", "ro.build.version.sdk"]
    assert len(SAFE_METADATA_PROPS) == 5
    with pytest.raises(ValueError):
        safe_prop_args("ro.serialno")
    with pytest.raises(ValueError):
        safe_prop_args("")


class _FakeSocket:
    def __init__(self) -> None:
        self.sent: list[dict[str, object]] = []

    async def send(self, message: str) -> None:
        self.sent.append(json.loads(message))


@pytest.fixture(autouse=True)
def _isolate(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("src.state.audit_logger.AUDIT_LOG", tmp_path / "audit.log")


def _fake_adb(devices_output: str) -> object:
    props = {
        "ro.build.version.release": "16",
        "ro.build.version.sdk": "36",
        "ro.build.fingerprint": "google/sdk/x:16/B/1:userdebug/dev-keys",
        "ro.product.manufacturer": "Google",
        "ro.product.model": "sdk_gphone64_x86_64",
    }

    def run(args: list[str], serial: str | None = None, **_: object) -> AdbResult:
        if args[0] == "devices":
            return AdbResult(devices_output.encode(), b"", 0)
        if args == ["shell", "id"]:
            return AdbResult(b"uid=2000(shell) gid=2000(shell)\n", b"", 0)
        return AdbResult(props[args[2]].encode() + b"\n", b"", 0)

    return run


@pytest.mark.asyncio
async def test_report_sent_only_when_list_changes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(device_detection, "run_adb", _fake_adb(_fixture("adb_devices_1.txt")))
    monkeypatch.setattr("src.device.privilege_detector.run_adb", device_detection.run_adb)
    socket, monitor = _FakeSocket(), DeviceMonitor(adb_path="adb")

    await monitor.poll_and_report(socket)
    await monitor.poll_and_report(socket)  # unchanged -> nothing sent
    assert len(socket.sent) == 1
    device = socket.sent[0]["devices"][0]  # type: ignore[index]
    assert device["serial"] == "emulator-5554"
    assert device["android_version"] == "16"
    assert device["api_level"] == 36
    assert device["privilege_state"] == "non_root"
    assert monitor.connected_count == 1

    monitor.reset_reporting()  # new connection -> full state again
    await monitor.poll_and_report(socket)
    assert len(socket.sent) == 2


@pytest.mark.asyncio
async def test_device_disappearing_is_reported_as_empty_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(device_detection, "run_adb", _fake_adb(_fixture("adb_devices_1.txt")))
    monkeypatch.setattr("src.device.privilege_detector.run_adb", device_detection.run_adb)
    socket, monitor = _FakeSocket(), DeviceMonitor(adb_path="adb")
    await monitor.poll_and_report(socket)

    monkeypatch.setattr(device_detection, "run_adb", _fake_adb(_fixture("adb_devices_0.txt")))
    await monitor.poll_and_report(socket)
    assert socket.sent[-1]["devices"] == []
    assert monitor.connected_count == 0
