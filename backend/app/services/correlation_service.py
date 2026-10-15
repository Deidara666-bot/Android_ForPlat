"""Start an analysis of a case: run the rule engine and commit the whole run (REF §ENGINE "Run").

The engine records a run inside one savepoint and never commits; this service is where the run
becomes durable. A run either stores every record or none: an error rolls the transaction back.
"""

import uuid
from collections.abc import Sequence
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.constants import EvidenceMode, RunPurpose
from app.models.case import Case
from app.research.engine.windows import RunWindow
from app.research.rule_engine import RuleEngine
from app.research.rules.loader import MANIFEST_PATH, RULES_DIR


class CaseNotFoundError(LookupError):
    """No case with that id."""


class CorrelationService:
    def __init__(
        self,
        db: Session,
        code_commit: str,
        *,
        rules_dir: Path = RULES_DIR,
        sources_path: Path | None = None,
        manifest_path: Path = MANIFEST_PATH,
    ) -> None:
        self.db = db
        self._engine = RuleEngine(
            db,
            code_commit=code_commit,
            rules_dir=rules_dir,
            sources_path=sources_path,
            manifest_path=manifest_path,
        )

    def analyze(
        self,
        case_id: uuid.UUID,
        evidence_mode: EvidenceMode,
        run_purpose: RunPurpose,
        window: RunWindow | None = None,
        subjects: Sequence[str] | None = None,
    ) -> uuid.UUID:
        """The id of the stored `CorrelationRun`. Raises the engine's errors unchanged."""
        if self.db.get(Case, case_id) is None:
            raise CaseNotFoundError(str(case_id))
        try:
            run_id = self._engine.run(case_id, evidence_mode, run_purpose, window, subjects)
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
        return run_id
