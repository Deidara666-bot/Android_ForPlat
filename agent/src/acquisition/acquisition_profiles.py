"""Named operation sequences. Operation IDs only; commands live in `src.device.adb_commands`."""

_G1_OPERATIONS = (
    "collect_device_metadata",
    "collect_package_inventory",
    "collect_package_detail",
    "collect_accessibility_state",
    "collect_usage_state",
    "pull_subject_apk",
)

PROFILES: dict[str, tuple[str, ...]] = {
    "baseline_v030": ("collect_device_metadata", "collect_package_inventory"),
    "g1_full": _G1_OPERATIONS,
    "tier2_g1": _G1_OPERATIONS,
}
