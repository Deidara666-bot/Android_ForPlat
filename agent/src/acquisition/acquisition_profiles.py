"""Named operation sequences. Operation IDs only; commands live in `src.device.adb_commands`."""

PROFILES: dict[str, tuple[str, ...]] = {
    "baseline_v030": ("collect_device_metadata", "collect_package_inventory"),
}
