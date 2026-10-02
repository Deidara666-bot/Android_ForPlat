from collections.abc import Mapping
from datetime import datetime
from types import MappingProxyType
from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from app.core.constants import EpistemicClass, EvidenceState, TemporalSemantics

# Closed catalog of 25 event types (REF §EVT, 02_ARSITEKTUR §Y.3.1a). No aliases, no legacy names.
EVENT_TYPE_CATALOG: Mapping[str, EpistemicClass] = MappingProxyType(
    {
        "package_observed_installed": EpistemicClass.identity_attribute,
        "uid_observed": EpistemicClass.identity_attribute,
        "apk_identity_observed": EpistemicClass.identity_attribute,
        "apk_endpoint_reference_observed": EpistemicClass.identity_attribute,
        "scenario_subject_binding_observed": EpistemicClass.identity_attribute,
        "synthetic_exclusion_marker_observed": EpistemicClass.identity_attribute,
        "permission_observed_requested": EpistemicClass.capability_state,
        "sensitive_communication_capability_observed_granted": EpistemicClass.capability_state,
        "sensitive_communication_capability_observed_declared": EpistemicClass.capability_state,
        "accessibility_service_observed_declared": EpistemicClass.capability_state,
        "special_access_capability_observed_enabled": EpistemicClass.capability_state,
        "special_access_capability_observed_declared": EpistemicClass.capability_state,
        "event_trigger_capability_observed_declared": EpistemicClass.capability_state,
        "service_observed_declared": EpistemicClass.capability_state,
        "event_trigger_execution_observed": EpistemicClass.execution_observed,
        "app_usage_observed": EpistemicClass.execution_observed,
        "activity_observed_resumed": EpistemicClass.execution_observed,
        "process_observed_running": EpistemicClass.execution_observed,
        "uid_network_activity_observed": EpistemicClass.execution_observed,
        "local_endpoint_request_observed": EpistemicClass.execution_observed,
        "lab_network_flow_observed": EpistemicClass.execution_observed,
        "sms_record_observed": EpistemicClass.data_present,
        "contact_record_observed": EpistemicClass.data_present,
        "call_log_record_observed": EpistemicClass.data_present,
        "notification_context_observed": EpistemicClass.data_present,
    }
)


class NormalizedFact(BaseModel):
    """One normalized claim before persistence; `id`, `case_id`, `artifact_id` are set on store."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_type: str
    epistemic_class: EpistemicClass
    subject_package: str | None
    subject_uid: int | None
    object_type: str
    object_value: str
    predicate_value: bool | None
    event_time: datetime | None
    observed_at: datetime
    window_start: datetime | None
    window_end: datetime | None
    temporal_semantics: TemporalSemantics
    evidence_state: EvidenceState
    context_json: dict[str, object]

    @field_validator("event_type")
    @classmethod
    def _event_type_in_catalog(cls, value: str) -> str:
        if value not in EVENT_TYPE_CATALOG:
            raise ValueError(f"event_type {value!r} is not in the closed catalog")
        return value

    @model_validator(mode="after")
    def _datetimes_are_aware(self) -> Self:
        for name in ("event_time", "observed_at", "window_start", "window_end"):
            value = getattr(self, name)
            if value is not None and value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware")
        return self
