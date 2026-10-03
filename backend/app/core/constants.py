from enum import StrEnum


class AvailabilityStatus(StrEnum):
    acquired = "acquired"
    unavailable = "unavailable"
    denied = "denied"
    unsupported = "unsupported"
    failed = "failed"


class EpistemicClass(StrEnum):
    identity_attribute = "identity_attribute"
    capability_state = "capability_state"
    execution_observed = "execution_observed"
    data_present = "data_present"


class EvidenceState(StrEnum):
    observed_true = "observed_true"
    observed_false = "observed_false"
    unknown_unavailable = "unknown_unavailable"


class TemporalSemantics(StrEnum):
    historical_event = "historical_event"
    current_state = "current_state"
    aggregated_window = "aggregated_window"
    unknown = "unknown"


class SourceGroup(StrEnum):
    APP_SYSTEM_STATE = "APP_SYSTEM_STATE"
    SENSITIVE_COMMUNICATION = "SENSITIVE_COMMUNICATION"
    NETWORK_ACTIVITY = "NETWORK_ACTIVITY"


class ParseStatus(StrEnum):
    parsed = "parsed"
    failed = "failed"
    empty = "empty"


class ConnectionState(StrEnum):
    connected = "connected"
    disconnected = "disconnected"
    unknown = "unknown"


class SessionStatus(StrEnum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class AgentState(StrEnum):
    starting = "starting"
    config_loaded = "config_loaded"
    adb_validated = "adb_validated"
    registered = "registered"
    connected = "connected"
    disconnected = "disconnected"
    stopped = "stopped"


class PrivilegeState(StrEnum):
    non_root = "non_root"
    root_detected = "root_detected"
    unknown = "unknown"


class ActorType(StrEnum):
    user = "user"
    agent = "agent"
    system = "system"


class AuditEventType(StrEnum):
    job_issued = "job_issued"
    operation_rejected = "operation_rejected"
    upload_accepted = "upload_accepted"
    upload_rejected_mismatch = "upload_rejected_mismatch"
    upload_validation_failed = "upload_validation_failed"
    authentication_failed = "authentication_failed"
    request_validation_failed = "request_validation_failed"
    normalization_skipped = "normalization_skipped"
    normalization_failed = "normalization_failed"
    session_timezone_set = "session_timezone_set"


# Allowlisted operation IDs (REF §OPS); the agent keeps its own copy and maps the command.
ALLOWED_OPERATIONS: frozenset[str] = frozenset(
    {
        "collect_device_metadata",
        "collect_package_inventory",
        "collect_package_detail",
        "collect_usage_state",
        "collect_accessibility_state",
        "collect_sensitive_provider_data",
        "collect_network_stats",
        "pull_subject_apk",
    }
)
# Operations the agent can run today; the others are rejected as not mapped yet.
MAPPED_OPERATIONS: frozenset[str] = frozenset(
    {
        "collect_device_metadata",
        "collect_package_inventory",
        "collect_package_detail",
        "collect_accessibility_state",
    }
)

# Parameter names each operation requires (none for the others); values are validated by shape.
OPERATION_PARAMETERS: dict[str, tuple[str, ...]] = {
    "collect_package_detail": ("package_name",),
    "collect_accessibility_state": ("package_name",),
}
PACKAGE_NAME_PATTERN = r"^[A-Za-z0-9_.]{1,200}$"

# Source group per operation (REF §OPS). NULL = context evidence that belongs to no group.
OPERATION_SOURCE_GROUP: dict[str, str | None] = {
    "collect_device_metadata": None,
    "collect_package_inventory": SourceGroup.APP_SYSTEM_STATE.value,
    "collect_package_detail": SourceGroup.APP_SYSTEM_STATE.value,
    "collect_accessibility_state": SourceGroup.APP_SYSTEM_STATE.value,
}

# Largest evidence file the upload endpoint accepts.
MAX_UPLOAD_BYTES = 50 * 1024 * 1024

# Named operation sequences a session may request (the agent keeps the same profile table).
ACQUISITION_PROFILES: dict[str, tuple[str, ...]] = {
    "baseline_v030": ("collect_device_metadata", "collect_package_inventory"),
}

# Order in which a failed acquisition is classified (first match wins, remainder is `failed`).
AVAILABILITY_CHECK_ORDER = (
    AvailabilityStatus.unsupported,
    AvailabilityStatus.denied,
    AvailabilityStatus.unavailable,
    AvailabilityStatus.failed,
)

# Indonesian UI labels (01_BREAKDOWN 4.7). Nested per enum: StrEnum members of different enums
# with the same value (e.g. `unknown`) would collide in one flat dict.
LABEL_ID: dict[type[StrEnum], dict[str, str]] = {
    AvailabilityStatus: {
        "acquired": "diperoleh",
        "unavailable": "tidak tersedia",
        "denied": "ditolak",
        "unsupported": "tidak didukung",
        "failed": "gagal",
    },
    EpistemicClass: {
        "identity_attribute": "atribut identitas",
        "capability_state": "kapabilitas",
        "execution_observed": "eksekusi teramati",
        "data_present": "keberadaan data",
    },
}


APP_VERSION = "0.10.0"
