import hashlib
import stat
import uuid
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.routes.evidence import get_evidence_storage
from app.core import constants
from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.user import User
from app.services.agent_service import AgentService
from app.services.evidence_storage_service import EvidenceStorageService

_DATA = b"package:com.example uid:10001\r\npackage:com.other uid:10002\n"
_OPERATION = "collect_package_inventory"


@pytest.fixture
def root(tmp_path: Path) -> Path:
    return tmp_path / "evidence_root"


@pytest.fixture(autouse=True)
def storage_in_tmp(client: TestClient, root: Path) -> Iterator[None]:
    from app.main import app

    app.dependency_overrides[get_evidence_storage] = lambda: EvidenceStorageService(root)
    yield
    app.dependency_overrides.pop(get_evidence_storage, None)


@pytest.fixture
def agent_token(session: Session) -> str:
    return AgentService(session).register("dev-agent-01", "0.20.0")


@pytest.fixture
def agent_headers(agent_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {agent_token}"}


@pytest.fixture
def acquisition(session: Session, user: User, agent_token: str) -> AcquisitionSession:
    agent = AgentService(session).find_by_token(agent_token)
    assert agent is not None
    case = Case(case_number="C-0001", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=datetime.now(UTC),
    )
    session.add_all([case, device])
    session.flush()
    row = AcquisitionSession(
        case_id=case.id,
        device_id=device.id,
        agent_id=agent.id,
        agent_version="0.20.0",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        started_at=datetime.now(UTC),
        timezone="unknown",
        status="running",
    )
    session.add(row)
    session.flush()
    session.add(AcquisitionOperation(session_id=row.id, sequence=1, operation_id=_OPERATION))
    session.commit()
    return row


def _fields(
    acquisition: AcquisitionSession, data: bytes = _DATA, **overrides: Any
) -> dict[str, Any]:
    fields: dict[str, Any] = {
        "session_id": str(acquisition.id),
        "operation_id": _OPERATION,
        "sequence": "1",
        "part": "1",
        "sha256_agent": hashlib.sha256(data).hexdigest(),
        "size_bytes": str(len(data)),
        "acquired_at": datetime.now(UTC).isoformat(),
        "raw_source": "pm list packages -U",
        "tool_version": "Android Debug Bridge version 1.0.41",
        "android_version": "16",
        "device_build": "BUILD",
        "privilege_state": "non_root",
    }
    fields.update(overrides)
    return fields


def _upload(
    client: TestClient,
    headers: dict[str, str],
    acquisition: AcquisitionSession,
    data: bytes = _DATA,
    filename: str = "evidence.bin",
    **overrides: Any,
) -> Any:
    return client.post(
        "/api/evidence/upload",
        headers=headers,
        data=_fields(acquisition, data, **overrides),
        files={"file": (filename, data, "application/octet-stream")},
    )


def _files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file()) if root.exists() else []


def test_upload_without_token_is_401(client: TestClient, acquisition: AcquisitionSession) -> None:
    assert _upload(client, {}, acquisition).status_code == 401


def test_examiner_jwt_cannot_upload(
    client: TestClient, auth_headers: dict[str, str], acquisition: AcquisitionSession
) -> None:
    assert _upload(client, auth_headers, acquisition).status_code == 401


def test_matching_hash_stores_the_file_and_records_both_hashes(
    client: TestClient,
    session: Session,
    agent_headers: dict[str, str],
    acquisition: AcquisitionSession,
    root: Path,
) -> None:
    response = _upload(client, agent_headers, acquisition)
    assert response.status_code == 201, response.text
    body = response.json()
    assert "stored_path" not in body
    digest = hashlib.sha256(_DATA).hexdigest()
    assert body["sha256_agent"] == body["sha256_server"] == digest
    assert body["availability_status"] == "acquired"
    assert body["source_group"] == "APP_SYSTEM_STATE"
    assert body["source_name"] == _OPERATION
    assert body["raw_source"] == "pm list packages -U"

    expected = root / str(acquisition.id) / f"1-{_OPERATION}-1.bin"
    assert expected.read_bytes() == _DATA  # byte-exact, CRLF untouched
    assert stat.S_IMODE(expected.stat().st_mode) & 0o222 == 0  # read-only
    row = session.scalar(select(Evidence))
    assert row is not None
    assert row.stored_path == f"{acquisition.id}/1-{_OPERATION}-1.bin"
    assert row.case_id == acquisition.case_id and row.device_id == acquisition.device_id


def test_metadata_operation_has_no_source_group(
    client: TestClient,
    session: Session,
    agent_headers: dict[str, str],
    acquisition: AcquisitionSession,
) -> None:
    session.add(
        AcquisitionOperation(
            session_id=acquisition.id, sequence=2, operation_id="collect_device_metadata"
        )
    )
    session.commit()
    response = _upload(
        client,
        agent_headers,
        acquisition,
        sequence="2",
        operation_id="collect_device_metadata",
        raw_source="getprop",
    )
    assert response.status_code == 201
    assert response.json()["source_group"] is None


def test_wrong_hash_is_rejected_recorded_as_failed_and_not_stored(
    client: TestClient,
    session: Session,
    agent_headers: dict[str, str],
    acquisition: AcquisitionSession,
    root: Path,
) -> None:
    fake = "0" * 64
    response = _upload(client, agent_headers, acquisition, sha256_agent=fake)
    assert response.status_code == 422
    assert response.json()["detail"]["jenis"] == "Sha256Mismatch"

    assert _files(root) == []
    row = session.scalar(select(Evidence))
    assert row is not None
    assert row.availability_status == "failed"
    assert row.availability_reason == "sha256 mismatch"
    assert row.stored_path is None
    assert row.sha256_agent == fake
    assert row.sha256_server == hashlib.sha256(_DATA).hexdigest()
    assert row.sha256_agent != row.sha256_server  # the server never copies the agent's digest


def test_second_upload_for_same_session_sequence_part_fails_and_keeps_old_file(
    client: TestClient,
    session: Session,
    agent_headers: dict[str, str],
    acquisition: AcquisitionSession,
    root: Path,
) -> None:
    assert _upload(client, agent_headers, acquisition).status_code == 201
    other = b"different bytes"
    response = _upload(client, agent_headers, acquisition, data=other)
    assert response.status_code == 409

    stored = root / str(acquisition.id) / f"1-{_OPERATION}-1.bin"
    assert stored.read_bytes() == _DATA
    assert session.scalar(select(func.count()).select_from(Evidence)) == 1


def test_client_file_name_cannot_choose_where_bytes_go(
    client: TestClient,
    agent_headers: dict[str, str],
    acquisition: AcquisitionSession,
    root: Path,
    tmp_path: Path,
) -> None:
    response = _upload(client, agent_headers, acquisition, filename="../../evil.txt")
    assert response.status_code == 201
    names = [path.relative_to(root).as_posix() for path in _files(root)]
    assert names == [f"{acquisition.id}/1-{_OPERATION}-1.bin"]
    assert not (tmp_path.parent / "evil.txt").exists()
    assert not (tmp_path / "evil.txt").exists()


def test_wrong_size_is_422_and_leaves_no_row_or_file(
    client: TestClient,
    session: Session,
    agent_headers: dict[str, str],
    acquisition: AcquisitionSession,
    root: Path,
) -> None:
    response = _upload(client, agent_headers, acquisition, size_bytes=str(len(_DATA) + 1))
    assert response.status_code == 422
    assert _files(root) == []
    assert session.scalar(select(func.count()).select_from(Evidence)) == 0


def test_operation_that_does_not_match_the_sequence_is_422(
    client: TestClient, agent_headers: dict[str, str], acquisition: AcquisitionSession, root: Path
) -> None:
    response = _upload(client, agent_headers, acquisition, operation_id="collect_device_metadata")
    assert response.status_code == 422
    assert _files(root) == []


def test_unknown_sequence_is_422(
    client: TestClient, agent_headers: dict[str, str], acquisition: AcquisitionSession
) -> None:
    assert _upload(client, agent_headers, acquisition, sequence="9").status_code == 422


def test_malformed_hash_is_422(
    client: TestClient, agent_headers: dict[str, str], acquisition: AcquisitionSession
) -> None:
    assert _upload(client, agent_headers, acquisition, sha256_agent="abc").status_code == 422


def test_naive_acquired_at_is_422(
    client: TestClient, agent_headers: dict[str, str], acquisition: AcquisitionSession
) -> None:
    response = _upload(client, agent_headers, acquisition, acquired_at="2026-10-02T10:00:00")
    assert response.status_code == 422


def test_session_of_another_agent_is_not_found(
    client: TestClient, session: Session, acquisition: AcquisitionSession
) -> None:
    other_token = AgentService(session).register("other-agent", "0.20.0")
    response = _upload(client, {"Authorization": f"Bearer {other_token}"}, acquisition)
    assert response.status_code == 404


def test_unknown_session_is_404(
    client: TestClient, agent_headers: dict[str, str], acquisition: AcquisitionSession
) -> None:
    response = _upload(client, agent_headers, acquisition, session_id=str(uuid.uuid4()))
    assert response.status_code == 404


def test_finished_session_does_not_accept_evidence(
    client: TestClient,
    session: Session,
    agent_headers: dict[str, str],
    acquisition: AcquisitionSession,
) -> None:
    acquisition.status = "completed"
    session.commit()
    assert _upload(client, agent_headers, acquisition).status_code == 404


def test_file_over_the_limit_is_413(
    client: TestClient,
    agent_headers: dict[str, str],
    acquisition: AcquisitionSession,
    root: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(constants, "MAX_UPLOAD_BYTES", 10)
    response = _upload(client, agent_headers, acquisition)
    assert response.status_code == 413
    assert _files(root) == []


def test_storage_refuses_a_key_that_could_escape_the_root(tmp_path: Path) -> None:
    storage = EvidenceStorageService(tmp_path / "root")
    for operation_id in ("../x", "a/b", "A", "", "x" * 80):
        with pytest.raises(ValueError):
            storage.store(uuid.uuid4(), 1, operation_id, 1, b"x")
    with pytest.raises(ValueError):
        storage.store(uuid.uuid4(), 0, "collect_device_metadata", 1, b"x")
