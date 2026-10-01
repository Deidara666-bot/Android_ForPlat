"""The only place ADB command strings may live (always as argument lists, never shell strings)."""

# Not allowlisted acquisition operations: device discovery, version check, privilege probe.
DEVICE_LIST: list[str] = ["devices", "-l"]
VERSION: list[str] = ["version"]
PRIVILEGE_PROBE: list[str] = ["shell", "id"]

# Operation ID -> adb arguments (after `-s <serial>`). Empty until v0.30.3 maps the first two.
OPERATION_ARGS: dict[str, list[str]] = {}
