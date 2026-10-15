"""Fixtures shared by the coverage tests: a case with a device and agent, and builders for
acquisition sessions, evidence rows and artifacts."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from sqlalchemy.orm import Session

from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.agent import Agent
from app.models.artifact import Artifact
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.user import User

_T0 = datetime(2026, 10, 3, 12, 0, tzinfo=UTC)


@pytest.fixture
def world(session: Session, user: User) -> dict[str, Any]:
    case = Case(case_number="C-COV-1", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_T0,
    )
    agent = Agent(agent_id="agent-cov", version="0.1.0")
    session.add_all([case, device, agent])
    session.flush()
    return {"case": case, "device": device, "agent": agent}


@pytest.fixture
def new_session(session: Session, world: dict[str, Any]) -> Callable[..., AcquisitionSession]:
    counter = {"n": 0}

    def make(operations: dict[str, dict[str, str]], status: str = "running") -> AcquisitionSession:
        counter["n"] += 1
        row = AcquisitionSession(
            case_id=world["case"].id,
            device_id=world["device"].id,
            agent_id=world["agent"].id,
            agent_version="0.1.0",
            android_version="16",
            api_level=36,
            device_build="BUILD",
            started_at=_T0 + timedelta(minutes=counter["n"]),
            timezone="unknown",
            status=status,
        )
        session.add(row)
        session.flush()
        for index, (operation, parameters) in enumerate(operations.items(), start=1):
            session.add(
                AcquisitionOperation(
                    session_id=row.id,
                    sequence=index,
                    operation_id=operation,
                    parameters=parameters,
                )
            )
        session.flush()
        return row

    return make


@pytest.fixture
def add_evidence(session: Session, world: dict[str, Any]) -> Callable[..., Evidence]:
    def make(acquisition: AcquisitionSession, operation: str, raw_source: str, **o: Any) -> Any:
        status = o.pop("availability_status", "acquired")
        values: dict[str, Any] = {
            "case_id": world["case"].id,
            "device_id": world["device"].id,
            "acquisition_session_id": acquisition.id,
            "operation_id": operation,
            "source_name": operation,
            "raw_source": raw_source,
            "acquired_at": _T0,
            "availability_status": status,
            "availability_reason": None if status == "acquired" else "uji",
        }
        values.update(o)
        row = Evidence(**values)
        session.add(row)
        session.flush()
        return row

    return make


@pytest.fixture
def add_artifact(session: Session) -> Callable[..., Artifact]:
    def make(evidence: Evidence, status: str = "parsed", **o: Any) -> Artifact:
        values: dict[str, Any] = {
            "evidence_id": evidence.id,
            "artifact_type": "settings_secure_list",
            "parser_name": "settings_state.secure",
            "parser_version": "1",
            "subject_key": None,
            "raw_value": "null",
            "parsed_value_json": {},
            "parse_status": status,
            "parse_note": "",
        }
        values.update(o)
        row = Artifact(**values)
        session.add(row)
        session.flush()
        return row

    return make
