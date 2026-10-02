from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.acquisition_session import AcquisitionSession
from app.models.agent import Agent
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.user import User

_NOW = datetime(2026, 10, 2, tzinfo=UTC)


@pytest.fixture
def parents(session: Session, user: User) -> dict[str, Any]:
    """Valid case/device/agent/session rows that every evidence row can point at."""
    case = Case(case_number="C-0001", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_NOW,
    )
    agent = Agent(agent_id="agent-uji", version="0.1.0")
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
    return {"case": case, "device": device, "agent": agent, "acquisition": acquisition}


@pytest.fixture
def make_evidence(parents: dict[str, Any]) -> Callable[..., Evidence]:
    def build(**overrides: Any) -> Evidence:
        values: dict[str, Any] = {
            "case_id": parents["case"].id,
            "device_id": parents["device"].id,
            "acquisition_session_id": parents["acquisition"].id,
            "operation_id": "collect_package_inventory",
            "source_group": "APP_SYSTEM_STATE",
            "source_name": "collect_package_inventory",
            "raw_source": "pm list packages -U",
            "acquired_at": _NOW,
            "availability_status": "acquired",
        }
        values.update(overrides)
        return Evidence(**values)

    return build


def _violated_constraint(session: Session, row: object) -> str:
    with pytest.raises(IntegrityError) as raised, session.begin_nested():
        session.add(row)
        session.flush()
    return raised.value.orig.diag.constraint_name  # type: ignore[union-attr]


def test_evidence_has_exactly_19_columns() -> None:
    assert len(Evidence.__table__.columns) == 19


def test_evidence_table_has_19_columns_in_database(session: Session) -> None:
    from sqlalchemy import text

    count = session.execute(
        text("select count(*) from information_schema.columns where table_name = 'evidence'")
    ).scalar_one()
    assert count == 19


def test_valid_row_is_accepted_and_server_hash_starts_null(
    session: Session, make_evidence: Callable[..., Evidence]
) -> None:
    row = make_evidence(sha256_agent="a" * 64)
    session.add(row)
    session.flush()
    assert row.sha256_server is None


def test_null_source_group_is_accepted(
    session: Session, make_evidence: Callable[..., Evidence]
) -> None:
    session.add(make_evidence(source_group=None, operation_id="collect_device_metadata"))
    session.flush()


def test_invalid_availability_status_names_its_constraint(
    session: Session, make_evidence: Callable[..., Evidence]
) -> None:
    row = make_evidence(availability_status="bogus", availability_reason="x")
    assert _violated_constraint(session, row) == "ck_evidence_availability_status"


def test_invalid_source_group_names_its_constraint(
    session: Session, make_evidence: Callable[..., Evidence]
) -> None:
    row = make_evidence(source_group="NOT_A_GROUP")
    assert _violated_constraint(session, row) == "ck_evidence_source_group"


def test_non_acquired_without_reason_names_its_constraint(
    session: Session, make_evidence: Callable[..., Evidence]
) -> None:
    row = make_evidence(availability_status="failed", availability_reason=None)
    assert _violated_constraint(session, row) == "ck_evidence_reason_required"


def test_non_acquired_with_reason_is_accepted(
    session: Session, make_evidence: Callable[..., Evidence]
) -> None:
    session.add(
        make_evidence(availability_status="denied", availability_reason="Permission denial")
    )
    session.flush()


def test_invalid_session_status_names_its_constraint(
    session: Session, parents: dict[str, Any]
) -> None:
    other = AcquisitionSession(
        case_id=parents["case"].id,
        device_id=parents["device"].id,
        agent_id=parents["agent"].id,
        agent_version="0.1.0",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        started_at=_NOW,
        timezone="UTC",
        status="bogus",
    )
    assert _violated_constraint(session, other) == "ck_acquisition_sessions_status"
