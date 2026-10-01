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
