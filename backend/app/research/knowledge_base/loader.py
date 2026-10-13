"""Load the knowledge-base sources into `kb_sources` (idempotent upsert by id)."""

import argparse
import hashlib
import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]
from sqlalchemy.orm import Session

from app.models.kb_source import KbSource
from app.research.knowledge_base.validator import (
    KbSourceEntry,
    KnowledgeBaseError,
    validate_sources,
)

SOURCES_PATH = Path(__file__).parent / "data" / "sources.yaml"


class KnowledgeBaseLoader:
    def __init__(self, path: Path = SOURCES_PATH) -> None:
        self.path = path

    def read(self) -> list[KbSourceEntry]:
        """Parse and validate the file; nothing is written."""
        try:
            data = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        except yaml.YAMLError as error:
            raise KnowledgeBaseError(f"{self.path.name}: not valid YAML: {error}") from error
        return validate_sources(data)

    def content_hash(self) -> str:
        """`KnowledgeBase.hash`: SHA-256 of the bytes of `sources.yaml`."""
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def load_to_db(self, db: Session) -> int:
        """Insert missing sources and update changed ones; flushes, never commits."""
        entries = self.read()
        for entry in entries:
            values = entry.model_dump()
            row = db.get(KbSource, entry.id)
            if row is None:
                db.add(KbSource(**values, active=True))
                continue
            for name, value in values.items():
                setattr(row, name, value)
        db.flush()
        return len(entries)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Load knowledge-base sources into the database.")
    parser.add_argument("--path", type=Path, default=SOURCES_PATH)
    args = parser.parse_args(argv)

    from app.db.session import SessionLocal

    with SessionLocal() as db:
        try:
            count = KnowledgeBaseLoader(args.path).load_to_db(db)
        except KnowledgeBaseError as error:
            sys.stderr.write(f"knowledge base not loaded: {error}\n")
            return 1
        db.commit()
    sys.stdout.write(f"loaded {count} knowledge-base sources\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
