import hashlib
import json
from datetime import UTC, datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.routes.evidence import get_evidence_storage
from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.audit_log import AuditLog
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.user import User
from app.services.agent_service import AgentService
from app.services.evidence_storage_service import EvidenceStorageService

_SERIAL = "emulator-5554"
_DATA = b"package:com.example uid:10001\n"
_OP = "collect_package_inventory"


@pytest.fixture(autouse=True)
def storage_in_tmp(client: TestClient, tmp_path: Any) -> Any:
    from app.main import app

    app.dependency_overrides[get_evidence_storage] = lambda: EvidenceStorageService(tmp_path / "ev")
    yield
    app.dependency_overrides.pop(get_evidence_storage, None)


@pytest.fixture
def agent_token(session: Session) -> str:
    return AgentService(session).register("dev-agent-01", "0.20.0")


@pytest.fixture
def setup(session: Session, user: User, agent_token: str) -> dict[str, Any]:
    agent = AgentService(session).find_by_token(agent_token)
    assert agent is not None
    case = Case(case_number="C-0001", title="uji", created_by=user.id)
    device = Device(
        serial=_SERIAL,
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        connection_state="connected",
        last_agent_id=agent.id,
        last_seen_at=datetime.now(UTC),
    )
    session.add_all([case, device])
    session.flush()
    return {"agent": agent, "case": case, "device": device}


def _events(session: Session) -> list[str]:
    return list(session.scalars(select(AuditLog.event_type).order_by(AuditLog.occurred_at)))


def _start(client: TestClient, headers: dict[str, str], setup: dict[str, Any], **body: str) -> Any:
    return client.post(
        "/api/acquisitions",
        headers=headers,
        json={"case_id": str(setup["case"].id), "device_id": str(setup["device"].id), **body},
    )


def _fields(session_id: str, data: bytes = _DATA, **overrides: Any) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "session_id": session_id,
        "operation_id": _OP,
        "sequence": "2",
        "part": "1",
        "sha256_agent": hashlib.sha256(data).hexdigest(),
        "size_bytes": str(len(data)),
        "acquired_at": datetime.now(UTC).isoformat(),
        "raw_source": "pm list packages -U",
    }
    fields.update(overrides)
    return fields


def _upload(client: TestClient, token: str, session_id: str, data: bytes = _DATA, **o: Any) -> Any:
    return client.post(
        "/api/evidence/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=_fields(session_id, data, **o),
        files={"file": ("x.bin", data, "application/octet-stream")},
    )


def test_job_issued_is_audited_for_each_operation(
    client: TestClient,
    session: Session,
    auth_headers: dict[str, str],
    setup: dict[str, Any],
    agent_token: str,
) -> None:
    with client.websocket_connect(
        "/ws/agent", headers={"Authorization": f"Bearer {agent_token}"}
    ) as ws:
        response = _start(client, auth_headers, setup, profile="baseline_v030")
        assert response.status_code == 201
        ws.receive_json()
        ws.receive_json()
    rows = list(session.scalars(select(AuditLog).where(AuditLog.event_type == "job_issued")))
    assert [(r.actor_type, r.object_type) for r in rows] == [("user", "acquisition_session")] * 2
    assert [r.details["sequence"] for r in rows] == [1, 2]
    assert {r.details["operation"] for r in rows} == {
        "collect_device_metadata",
        "collect_package_inventory",
    }


def test_rejected_operation_id_is_audited_even_though_the_request_fails(
    client: TestClient, session: Session, auth_headers: dict[str, str], setup: dict[str, Any]
) -> None:
    for operation in ("collect_usage_state", "collect_everything"):
        assert _start(client, auth_headers, setup, operation=operation).status_code == 422
    rows = list(
        session.scalars(select(AuditLog).where(AuditLog.event_type == "operation_rejected"))
    )
    assert sorted(r.reason for r in rows if r.reason) == [
        "OperationNotAllowedError",
        "OperationNotMappedError",
    ]
    assert all(r.actor_type == "user" for r in rows)


@pytest.fixture
def running_session(session: Session, setup: dict[str, Any]) -> AcquisitionSession:
    acquisition = AcquisitionSession(
        case_id=setup["case"].id,
        device_id=setup["device"].id,
        agent_id=setup["agent"].id,
        agent_version="0.20.0",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        started_at=datetime.now(UTC),
        timezone="unknown",
        status="running",
    )
    session.add(acquisition)
    session.flush()
    session.add_all(
        [
            AcquisitionOperation(
                session_id=acquisition.id, sequence=1, operation_id="collect_device_metadata"
            ),
            AcquisitionOperation(session_id=acquisition.id, sequence=2, operation_id=_OP),
        ]
    )
    session.commit()
    return acquisition


def test_accepted_upload_is_audited(
    client: TestClient, session: Session, agent_token: str, running_session: AcquisitionSession
) -> None:
    assert _upload(client, agent_token, str(running_session.id)).status_code == 201
    row = session.scalar(select(AuditLog).where(AuditLog.event_type == "upload_accepted"))
    assert row is not None
    assert row.actor_type == "agent" and row.object_type == "evidence"
    assert row.details["sequence"] == 2 and row.details["size_bytes"] == len(_DATA)


def test_mismatch_upload_is_audited_with_both_digests(
    client: TestClient, session: Session, agent_token: str, running_session: AcquisitionSession
) -> None:
    fake = "0" * 64
    response = _upload(client, agent_token, str(running_session.id), sha256_agent=fake)
    assert response.status_code == 422
    row = session.scalar(select(AuditLog).where(AuditLog.event_type == "upload_rejected_mismatch"))
    assert row is not None
    assert row.reason == "sha256 mismatch"
    assert row.details["sha256_agent"] == fake
    assert row.details["sha256_server"] == hashlib.sha256(_DATA).hexdigest()


def test_failed_upload_validation_is_audited(
    client: TestClient, session: Session, agent_token: str, running_session: AcquisitionSession
) -> None:
    response = _upload(client, agent_token, str(running_session.id), size_bytes="1")
    assert response.status_code == 422
    row = session.scalar(select(AuditLog).where(AuditLog.event_type == "upload_validation_failed"))
    assert row is not None
    assert row.details["http_status"] == 422
    assert row.reason == "size_bytes does not match the uploaded length"
    assert session.scalar(select(Evidence.id)) is None  # validation failure leaves no evidence


def test_audit_details_never_hold_command_text(
    client: TestClient,
    session: Session,
    auth_headers: dict[str, str],
    setup: dict[str, Any],
    agent_token: str,
    running_session: AcquisitionSession,
) -> None:
    _start(client, auth_headers, setup, operation="collect_usage_state")
    _upload(client, agent_token, str(running_session.id))
    _upload(client, agent_token, str(running_session.id), size_bytes="1")
    text = json.dumps([row.details for row in session.scalars(select(AuditLog))])
    for fragment in ("getprop", "pm list", "dumpsys", "shell"):
        assert fragment not in text


def _report(session_id: str, sequence: int, operation: str, **extra: Any) -> dict[str, Any]:
    return {
        "type": "job_status",
        "session_id": session_id,
        "sequence": sequence,
        "part": 1,
        "parts_total": 1,
        "operation": operation,
        "serial": _SERIAL,
        "returncode": 255,
        **extra,
    }


@pytest.mark.parametrize("status", ["denied", "unsupported", "unavailable", "failed"])
def test_non_acquired_outcome_creates_an_evidence_row_with_status_and_reason(
    client: TestClient,
    session: Session,
    agent_token: str,
    running_session: AcquisitionSession,
    status: str,
) -> None:
    with client.websocket_connect(
        "/ws/agent", headers={"Authorization": f"Bearer {agent_token}"}
    ) as ws:
        ws.send_json(
            _report(
                str(running_session.id),
                2,
                _OP,
                availability_status=status,
                availability_reason="Permission Denial: x",
            )
        )
    row = session.scalar(select(Evidence).where(Evidence.availability_status == status))
    assert row is not None
    assert row.availability_reason == "Permission Denial: x"
    assert row.stored_path is None and row.sha256_agent is None and row.sha256_server is None
    assert row.source_group == "APP_SYSTEM_STATE"
    operation = session.scalar(
        select(AcquisitionOperation).where(
            AcquisitionOperation.session_id == running_session.id,
            AcquisitionOperation.sequence == 2,
        )
    )
    assert operation is not None and operation.status == "failed"


def test_unavailable_with_exit_code_zero_is_not_completed(
    client: TestClient,
    session: Session,
    agent_token: str,
    running_session: AcquisitionSession,
) -> None:
    with client.websocket_connect(
        "/ws/agent", headers={"Authorization": f"Bearer {agent_token}"}
    ) as ws:
        ws.send_json(
            _report(
                str(running_session.id),
                2,
                _OP,
                returncode=0,
                availability_status="unavailable",
                availability_reason="empty output",
            )
        )
    operation = session.scalar(
        select(AcquisitionOperation).where(
            AcquisitionOperation.session_id == running_session.id,
            AcquisitionOperation.sequence == 2,
        )
    )
    assert operation is not None and operation.status == "failed"


def test_mismatch_row_is_not_duplicated_by_the_following_failed_job_status(
    client: TestClient, session: Session, agent_token: str, running_session: AcquisitionSession
) -> None:
    _upload(client, agent_token, str(running_session.id), sha256_agent="0" * 64)
    with client.websocket_connect(
        "/ws/agent", headers={"Authorization": f"Bearer {agent_token}"}
    ) as ws:
        ws.send_json(
            _report(
                str(running_session.id),
                2,
                _OP,
                availability_status="failed",
                availability_reason="backend rejected the upload (HTTP 422)",
            )
        )
    rows = list(session.scalars(select(Evidence).where(Evidence.operation_id == _OP)))
    assert len(rows) == 1 and rows[0].availability_reason == "sha256 mismatch"


def test_missing_reason_is_not_invented_beyond_saying_it_was_not_reported(
    client: TestClient, session: Session, agent_token: str, running_session: AcquisitionSession
) -> None:
    with client.websocket_connect(
        "/ws/agent", headers={"Authorization": f"Bearer {agent_token}"}
    ) as ws:
        ws.send_json(_report(str(running_session.id), 2, _OP, availability_status="denied"))
    row = session.scalar(select(Evidence))
    assert row is not None and row.availability_reason == "reason not reported by agent"


def test_non_acquired_evidence_without_reason_names_the_reason_constraint(
    session: Session, running_session: AcquisitionSession
) -> None:
    bad = Evidence(
        case_id=running_session.case_id,
        device_id=running_session.device_id,
        acquisition_session_id=running_session.id,
        operation_id=_OP,
        source_name=_OP,
        raw_source=_OP,
        acquired_at=datetime.now(UTC),
        availability_status="denied",
        availability_reason=None,
    )
    with pytest.raises(IntegrityError) as raised, session.begin_nested():
        session.add(bad)
        session.flush()
    assert raised.value.orig.diag.constraint_name == "ck_evidence_reason_required"  # type: ignore[union-attr]
