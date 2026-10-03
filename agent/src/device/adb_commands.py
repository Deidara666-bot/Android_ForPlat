"""The only place ADB command strings may live (always as argument lists, never shell strings)."""

# Not allowlisted acquisition operations: device discovery, version check, privilege probe.
DEVICE_LIST: list[str] = ["devices", "-l"]
VERSION: list[str] = ["version"]
PRIVILEGE_PROBE: list[str] = ["shell", "id"]

# Operation ID -> adb arguments (after `-s <serial>`). `{name}` tokens are filled from the job's
# validated parameters (see OPERATION_PARAMETERS); no other substitution exists.
OPERATION_ARGS: dict[str, list[str]] = {
    "collect_device_metadata": ["shell", "getprop"],
    "collect_package_inventory": ["shell", "pm", "list", "packages", "-U"],
    "collect_package_detail": ["shell", "dumpsys", "package", "{package_name}"],
}

# Multi-command operations: ordered `(raw_source label, adb arguments)`, one evidence file per
# command (`part` 1..n). Same `{name}` substitution rules as OPERATION_ARGS.
OPERATION_PARTS: dict[str, list[tuple[str, list[str]]]] = {
    "collect_accessibility_state": [
        (
            "settings secure a11y",
            ["shell", "settings", "get", "secure", "enabled_accessibility_services"],
        ),
        (
            "settings secure nls",
            ["shell", "settings", "get", "secure", "enabled_notification_listeners"],
        ),
        ("appops overlay", ["shell", "appops", "get", "{package_name}", "SYSTEM_ALERT_WINDOW"]),
    ],
    "collect_usage_state": [
        ("dumpsys usagestats", ["shell", "dumpsys", "usagestats"]),
        ("dumpsys activity", ["shell", "dumpsys", "activity", "activities"]),
        ("ps", ["shell", "ps", "-A", "-o", "PID,UID,USER,NAME"]),
    ],
    # Parts 3.. of this operation are the static extractor's bundle files, not adb commands.
    # `{apk_path}` and `{local_path}` are filled by the runner (never from job parameters):
    # the first from the output of part 1, the second from the evidence path of part 2.
    "pull_subject_apk": [
        ("pm path", ["shell", "pm", "path", "{package_name}"]),
        ("apk file", ["pull", "{apk_path}", "{local_path}"]),
    ],
}

# Where a pulled APK may live on the device (REF §OPS2); anything else is refused.
APK_PATH_PATTERN = r"^/(data/app|system|product|system_ext)/[^\s]+\.apk$"

# Operation ID -> the exact parameter names the job must carry (none for the others).
OPERATION_PARAMETERS: dict[str, tuple[str, ...]] = {
    "collect_package_detail": ("package_name",),
    "collect_accessibility_state": ("package_name",),
    "pull_subject_apk": ("package_name",),
}

# Shape of a package name accepted as a parameter (REF §OPS2); no '-', so never an adb option.
PACKAGE_NAME_PATTERN = r"^[A-Za-z0-9_.]{1,200}$"

# Human-readable evidence source per operation, sent with the upload (a label, not a command).
RAW_SOURCE_LABEL: dict[str, str] = {
    "collect_device_metadata": "getprop",
    "collect_package_inventory": "pm list packages -U",
    "collect_package_detail": "dumpsys package",
}

# Read-only build properties reported with a device. Not evidence: no hash, no file.
SAFE_METADATA_PROPS: tuple[str, ...] = (
    "ro.build.version.release",
    "ro.build.version.sdk",
    "ro.build.fingerprint",
    "ro.product.manufacturer",
    "ro.product.model",
)


def safe_prop_args(prop: str) -> list[str]:
    """Argument list for reading one allowed property; anything else is refused."""
    if prop not in SAFE_METADATA_PROPS:
        raise ValueError(f"property {prop!r} is not in SAFE_METADATA_PROPS")
    return ["shell", "getprop", prop]
