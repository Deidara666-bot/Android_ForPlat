import hashlib
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import ParseStatus
from app.models.acquisition_session import AcquisitionSession
from app.models.agent import Agent
from app.models.artifact import Artifact
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.user import User
from app.parsing.base import ParsedArtifact
from app.services.artifact_service import ArtifactService

_NOW = datetime(2026, 10, 2, tzinfo=UTC)


def _evidence(session: Session, user: User) -> Evidence:
    case = Case(case_number="C-ART-1", title="uji", created_by=user.id)
    device = Device(
        serial="emulator-5554",
        manufacturer="Google",
        model="sdk",
        android_version="16",
        api_level=36,
        device_build="BUILD",
        last_seen_at=_NOW,
    )
    agent = Agent(agent_id="agent-art", version="0.1.0")
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
    row = Evidence(
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
    session.add(row)
    session.flush()
    return row


def _item(status: ParseStatus, note: str, raw: str) -> ParsedArtifact:
    return ParsedArtifact(
        artifact_type="package_inventory_entry",
        parser_name="package_state.inventory",
        parser_version="1",
        subject_key=None if status != ParseStatus.parsed else "com.synthetic.alpha",
        raw_value=raw,
        parsed_value_json={"line_no": 1},
        parse_status=status,
        parse_note=note,
    )


def test_artifacts_table_has_exactly_10_columns() -> None:
    assert len(Artifact.__table__.columns) == 10


def test_failed_artifact_is_stored_and_readable(session: Session, user: User) -> None:
    evidence = _evidence(session, user)
    items = [
        _item(ParseStatus.parsed, "", "package:com.synthetic.alpha uid:10101"),
        _item(ParseStatus.failed, "baris tidak sesuai bentuk", "paket-rusak-tanpa-uid"),
    ]
    stored = ArtifactService().store_artifacts(session, evidence.id, items)
    assert len(stored) == 2

    rows = session.scalars(select(Artifact).where(Artifact.evidence_id == evidence.id)).all()
    assert {row.parse_status for row in rows} == {"parsed", "failed"}
    failed = next(row for row in rows if row.parse_status == "failed")
    assert failed.parse_note == "baris tidak sesuai bentuk"
    assert failed.raw_value == "paket-rusak-tanpa-uid"


def test_reading_evidence_leaves_bytes_unchanged(tmp_path: Path) -> None:
    path = tmp_path / "1-collect_package_inventory-1.bin"
    path.write_bytes(b"package:a uid:1\r\n\x00tail")
    before = hashlib.sha256(path.read_bytes()).hexdigest()

    data = ArtifactService().read_evidence_bytes(path)

    assert data == b"package:a uid:1\r\n\x00tail"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before
