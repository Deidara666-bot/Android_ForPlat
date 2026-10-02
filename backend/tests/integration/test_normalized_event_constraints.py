import re
from datetime import UTC, datetime
from typing import Any

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.acquisition_session import AcquisitionSession
from app.models.agent import Agent
from app.models.artifact import Artifact
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.normalized_event import NormalizedEvent
from app.models.user import User
from app.normalization.event_schema import EVENT_TYPE_CATALOG

_NOW = datetime(2026, 10, 2, tzinfo=UTC)


@pytest.fixture
def parents(session: Session, user: User) -> dict[str, Any]:
    case = Case(case_number="C-NE-1", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_NOW,
    )
    agent = Agent(agent_id="agent-ne", version="0.1.0")
    session.add_all([case, device, agent])
    session.flush()
    acquisition = AcquisitionSession(
        case_id=case.id,
        device_id=device.id,
        agent_id=agent.id,
        agent_version="0.1.0",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        started_at=_NOW,
        timezone="UTC",
    )
    session.add(acquisition)
    session.flush()
    evidence = Evidence(
        case_id=case.id,
        device_id=device.id,
        acquisition_session_id=acquisition.id,
        operation_id="collect_package_inventory",
        source_group="APP_SYSTEM_STATE",
        source_name="collect_package_inventory",
        raw_source="pm list packages -U",
        acquired_at=_NOW,
        availability_status="acquired",
    )
    session.add(evidence)
    session.flush()
    artifact = Artifact(
        evidence_id=evidence.id,
        artifact_type="package_inventory_entry",
        parser_name="package_state.inventory",
        parser_version="1",
        subject_key="com.synthetic.alpha",
        raw_value="package:com.synthetic.alpha uid:10101",
        parsed_value_json={"line_no": 1},
        parse_status="parsed",
        parse_note="",
    )
    session.add(artifact)
    session.flush()
    return {"case": case, "artifact": artifact}


def _event(parents: dict[str, Any], **overrides: Any) -> NormalizedEvent:
    values: dict[str, Any] = {
        "case_id": parents["case"].id,
        "artifact_id": parents["artifact"].id,
        "event_type": "package_observed_installed",
        "epistemic_class": "identity_attribute",
        "subject_package": "com.synthetic.alpha",
        "subject_uid": 10101,
        "object_type": "package_name",
        "object_value": "com.synthetic.alpha",
        "predicate_value": True,
        "event_time": None,
        "observed_at": _NOW,
        "temporal_semantics": "current_state",
        "evidence_state": "observed_true",
        "context_json": {},
    }
    values.update(overrides)
    return NormalizedEvent(**values)


def _violated(session: Session, row: object) -> str:
    with pytest.raises(IntegrityError) as raised, session.begin_nested():
        session.add(row)
        session.flush()
    return raised.value.orig.diag.constraint_name  # type: ignore[union-attr]


def test_normalized_events_has_exactly_17_columns() -> None:
    assert len(NormalizedEvent.__table__.columns) == 17


def test_valid_row_with_null_event_time_accepted(session: Session, parents: dict[str, Any]) -> None:
    session.add(_event(parents))
    session.flush()


@pytest.mark.parametrize(
    ("override", "constraint"),
    [
        ({"event_type": "permission_observed_granted"}, "ck_normalized_events_event_type"),
        ({"epistemic_class": "bogus"}, "ck_normalized_events_epistemic_class"),
        ({"temporal_semantics": "bogus"}, "ck_normalized_events_temporal_semantics"),
        ({"evidence_state": "bogus"}, "ck_normalized_events_evidence_state"),
    ],
)
def test_each_check_names_its_constraint(
    session: Session, parents: dict[str, Any], override: dict[str, str], constraint: str
) -> None:
    assert _violated(session, _event(parents, **override)) == constraint


def test_event_type_check_values_equal_catalog(session: Session) -> None:
    definition = session.execute(
        text(
            "select pg_get_constraintdef(oid) from pg_constraint "
            "where conname = 'ck_normalized_events_event_type'"
        )
    ).scalar_one()
    assert set(re.findall(r"'([a-z_]+)'", definition)) == set(EVENT_TYPE_CATALOG)
