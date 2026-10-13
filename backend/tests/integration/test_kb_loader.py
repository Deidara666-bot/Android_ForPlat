from pathlib import Path

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.kb_source import KbSource
from app.research.knowledge_base.loader import SOURCES_PATH, KnowledgeBaseLoader
from app.research.knowledge_base.validator import KnowledgeBaseError


def _count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(KbSource)) or 0


def test_loading_the_shipped_file_gives_eleven_active_rows(session: Session) -> None:
    assert KnowledgeBaseLoader().load_to_db(session) == 11
    assert _count(session) == 11
    assert session.scalar(select(func.count()).where(KbSource.active.is_(True))) == 11
    row = session.get(KbSource, "KB-AND-OVERLAY")
    assert row is not None
    assert row.publisher == "Android Developers"
    assert row.version_scope is None and row.quality_note is None
    assert row.reference_role == "artifact_semantics"


def test_loading_twice_does_not_duplicate_and_restores_changed_fields(session: Session) -> None:
    loader = KnowledgeBaseLoader()
    loader.load_to_db(session)
    row = session.get(KbSource, "KB-MITRE-T1624")
    assert row is not None
    row.title = "edited by hand"
    session.flush()

    loader.load_to_db(session)

    assert _count(session) == 11
    session.refresh(row)
    assert row.title == "MITRE ATT&CK Mobile — Event Triggered Execution"


def test_an_invalid_file_writes_nothing(session: Session, tmp_path: Path) -> None:
    broken = tmp_path / "sources.yaml"
    broken.write_text(
        SOURCES_PATH.read_text(encoding="utf-8").replace(
            "reference_role: technique_mapping", "reference_role: evidence_score", 1
        ),
        encoding="utf-8",
    )
    with pytest.raises(KnowledgeBaseError, match="reference_role"):
        KnowledgeBaseLoader(broken).load_to_db(session)
    assert _count(session) == 0


def test_a_file_that_is_not_yaml_is_a_load_error(session: Session, tmp_path: Path) -> None:
    broken = tmp_path / "sources.yaml"
    broken.write_text("sources: [unclosed", encoding="utf-8")
    with pytest.raises(KnowledgeBaseError, match="not valid YAML"):
        KnowledgeBaseLoader(broken).load_to_db(session)


@pytest.mark.parametrize(
    ("column", "value", "constraint"),
    [
        ("reference_role", "evidence_score", "ck_kb_sources_reference_role"),
        ("verification_status", "trusted", "ck_kb_sources_verification_status"),
    ],
)
def test_the_database_rejects_values_outside_the_closed_enums(
    session: Session, column: str, value: str, constraint: str
) -> None:
    KnowledgeBaseLoader().load_to_db(session)
    with pytest.raises(IntegrityError, match=constraint), session.begin_nested():
        session.execute(
            text(f"update kb_sources set {column} = :v where id = 'KB-AND-PACKAGE'"), {"v": value}
        )
