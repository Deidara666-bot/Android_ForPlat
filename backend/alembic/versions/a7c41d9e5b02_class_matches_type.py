"""normalized event class matches type

Revision ID: a7c41d9e5b02
Revises: 0fc9d155262e
Create Date: 2026-10-02 23:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a7c41d9e5b02"
down_revision: str | Sequence[str] | None = "0fc9d155262e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Snapshot of REF section EVT (25 pairs); migrations must not import the live catalog.
_PAIRS = (
    ("package_observed_installed", "identity_attribute"),
    ("uid_observed", "identity_attribute"),
    ("apk_identity_observed", "identity_attribute"),
    ("apk_endpoint_reference_observed", "identity_attribute"),
    ("scenario_subject_binding_observed", "identity_attribute"),
    ("synthetic_exclusion_marker_observed", "identity_attribute"),
    ("permission_observed_requested", "capability_state"),
    ("sensitive_communication_capability_observed_granted", "capability_state"),
    ("sensitive_communication_capability_observed_declared", "capability_state"),
    ("accessibility_service_observed_declared", "capability_state"),
    ("special_access_capability_observed_enabled", "capability_state"),
    ("special_access_capability_observed_declared", "capability_state"),
    ("event_trigger_capability_observed_declared", "capability_state"),
    ("service_observed_declared", "capability_state"),
    ("event_trigger_execution_observed", "execution_observed"),
    ("app_usage_observed", "execution_observed"),
    ("activity_observed_resumed", "execution_observed"),
    ("process_observed_running", "execution_observed"),
    ("uid_network_activity_observed", "execution_observed"),
    ("local_endpoint_request_observed", "execution_observed"),
    ("lab_network_flow_observed", "execution_observed"),
    ("sms_record_observed", "data_present"),
    ("contact_record_observed", "data_present"),
    ("call_log_record_observed", "data_present"),
    ("notification_context_observed", "data_present"),
)


def upgrade() -> None:
    """Upgrade schema."""
    values = ", ".join(
        f"('{event_type}', '{epistemic_class}')" for event_type, epistemic_class in _PAIRS
    )
    op.create_check_constraint(
        op.f("ck_normalized_events_class_matches_type"),
        "normalized_events",
        f"(event_type, epistemic_class) IN ({values})",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        op.f("ck_normalized_events_class_matches_type"), "normalized_events", type_="check"
    )
