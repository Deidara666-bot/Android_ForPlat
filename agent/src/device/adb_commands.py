"""The only place ADB command strings may live (always as argument lists, never shell strings)."""

# Not allowlisted acquisition operations: device discovery, version check, privilege probe.
DEVICE_LIST: list[str] = ["devices", "-l"]
VERSION: list[str] = ["version"]
PRIVILEGE_PROBE: list[str] = ["shell", "id"]

# Operation ID -> adb arguments (after `-s <serial>`). Only the first two are mapped (v0.30.3).
OPERATION_ARGS: dict[str, list[str]] = {
    "collect_device_metadata": ["shell", "getprop"],
    "collect_package_inventory": ["shell", "pm", "list", "packages", "-U"],
}

# Human-readable evidence source per operation, sent with the upload (a label, not a command).
RAW_SOURCE_LABEL: dict[str, str] = {
    "collect_device_metadata": "getprop",
    "collect_package_inventory": "pm list packages -U",
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
