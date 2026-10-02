import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.artifact import Artifact
from app.parsing.base import ParsedArtifact


class ArtifactService:
    """Reads stored evidence (never writes it) and persists parser output."""

    def read_evidence_bytes(self, stored_path: str | Path) -> bytes:
        with open(stored_path, "rb") as handle:
            return handle.read()

    def store_artifacts(
        self, session: Session, evidence_id: uuid.UUID, items: list[ParsedArtifact]
    ) -> list[Artifact]:
        rows = [
            Artifact(
                evidence_id=evidence_id,
                artifact_type=item.artifact_type,
                parser_name=item.parser_name,
                parser_version=item.parser_version,
                subject_key=item.subject_key,
                raw_value=item.raw_value,
                parsed_value_json=dict(item.parsed_value_json),
                parse_status=item.parse_status.value,
                parse_note=item.parse_note,
            )
            for item in items
        ]
        session.add_all(rows)
        session.flush()
        return rows
