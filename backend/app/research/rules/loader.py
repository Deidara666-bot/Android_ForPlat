"""Load validated rule families into `rule_metadata` (02_ARSITEKTUR sections Z.0.2, AG.11).

Order: read every `family.yaml` -> validate (schema, then section Z.0) -> status gate for the run
purpose (and, for `holdout`, knowledge-base completeness, then the freeze manifest) -> write.
A refusal at any step writes nothing. Rows are insert-only per `content_hash`: a file whose hash is
already stored is not written again, an older version stays. The *active* rows are the ones that
belong to the `RuleSet` just loaded.
"""

import argparse
import hashlib
import json
import sys
import uuid
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import RuleStatus, RunPurpose
from app.models.kb_source import KbSource
from app.models.rule_metadata import RuleElementReference, RuleMetadata, RuleReference
from app.research.knowledge_base.loader import KnowledgeBaseLoader
from app.research.rules.errors import RuleLoadError, RuleLoadErrorCode
from app.research.rules.schema import RuleFamilyFile
from app.research.rules.validator import RuleValidator, parse_family_text

RULES_DIR = Path(__file__).parent / "data" / "apk_fraud"
FAMILY_IDS = tuple(
    f"APKF-K0{number}" for number in range(1, 6)
)  # the closed set (REF section YAML)
MANIFEST_PATH = Path(__file__).resolve().parents[4] / "experiments" / "freeze_manifest.json"

_ALLOWED_STATUS: dict[RunPurpose, frozenset[RuleStatus]] = {
    RunPurpose.authoring: frozenset({RuleStatus.design_baseline, RuleStatus.authoring_candidate}),
    RunPurpose.benign_control: frozenset(
        {RuleStatus.design_baseline, RuleStatus.authoring_candidate}
    ),
    RunPurpose.holdout: frozenset({RuleStatus.frozen_for_holdout}),
    RunPurpose.production: frozenset(
        {RuleStatus.authoring_candidate, RuleStatus.frozen_for_holdout}
    ),
}


@dataclass(frozen=True)
class LoadedFamily:
    """One family as loaded; `row_ids` maps `None` (family row) and each `profile_id` to its row."""

    family_id: str
    version: int
    status: str
    content_hash: str
    row_ids: Mapping[str | None, uuid.UUID]
    family_file: RuleFamilyFile  # the parsed YAML: conditions are not stored in the database


@dataclass(frozen=True)
class RuleSet:
    run_purpose: RunPurpose | None  # None: loaded by `load_validated`, never usable for an analysis
    hash: str  # combined hash of the family files, see `combine_hashes`
    kb_hash: str  # `KnowledgeBase.hash`
    families: tuple[LoadedFamily, ...]


@dataclass(frozen=True)
class _Source:
    path: Path
    raw: bytes
    family_file: RuleFamilyFile

    @property
    def content_hash(self) -> str:
        return hashlib.sha256(self.raw).hexdigest()


def combine_hashes(content_hashes: Mapping[str, str]) -> str:
    """`RuleSet.hash`: SHA-256 over `family_id:hash` lines, sorted by `family_id`."""
    lines = (f"{family_id}:{content_hashes[family_id]}\n" for family_id in sorted(content_hashes))
    return hashlib.sha256("".join(lines).encode("ascii")).hexdigest()


class RuleLoader:
    def __init__(
        self,
        db: Session,
        *,
        rules_dir: Path = RULES_DIR,
        sources_path: Path | None = None,
        manifest_path: Path = MANIFEST_PATH,
    ) -> None:
        self.db = db
        self.rules_dir = rules_dir
        self.knowledge_base = (
            KnowledgeBaseLoader(sources_path) if sources_path else KnowledgeBaseLoader()
        )
        self.manifest_path = manifest_path

    def load_all(self, run_purpose: RunPurpose | str) -> RuleSet:
        """Validate, gate and store every family for `run_purpose`; flushes, never commits.

        Used once per analysis. `run_purpose` is required: the gate cannot be skipped by passing
        nothing (use `load_validated` for the startup load, which has no run).
        """
        if run_purpose is None:
            raise ValueError(
                "run_purpose is required; load_validated() is the ungated startup load"
            )
        return self._load(RunPurpose(run_purpose))

    def load_validated(self) -> RuleSet:
        """Validate and store every family without the run-purpose gate (startup, display only).

        The `RuleSet` has `run_purpose=None`; an analysis must not use it.
        """
        return self._load(None)

    def _load(self, purpose: RunPurpose | None) -> RuleSet:
        active_sources = list(self.db.scalars(select(KbSource).where(KbSource.active.is_(True))))
        validator = RuleValidator({source.id: source for source in active_sources})
        sources = self._read_sources()
        validator.validate_all([source.family_file for source in sources])

        kb_hash = self.knowledge_base.content_hash()
        if purpose is not None:
            self._check_status(purpose, sources)
            if purpose == RunPurpose.holdout:
                self._check_knowledge_base_complete(active_sources)
                self._check_manifest(sources, kb_hash)

        loaded = tuple(self._store(source, validator) for source in sources)
        hashes = {family.family_id: family.content_hash for family in loaded}
        return RuleSet(purpose, combine_hashes(hashes), kb_hash, loaded)

    def _read_sources(self) -> list[_Source]:
        """The closed family set: exactly `APKF-K01`..`K05`, each folder named like its family."""
        schema_invalid = RuleLoadErrorCode.schema_invalid
        present = (
            {entry.name for entry in self.rules_dir.iterdir() if entry.is_dir()}
            if self.rules_dir.is_dir()
            else set()
        )
        for name in FAMILY_IDS:
            if name not in present:
                raise RuleLoadError(schema_invalid, name, "family directory is missing")
        for name in sorted(present - set(FAMILY_IDS)):
            raise RuleLoadError(schema_invalid, name, "not one of the five family directories")
        sources = []
        for name in FAMILY_IDS:
            path = self.rules_dir / name / "family.yaml"
            where = f"{name}/family.yaml"
            if not path.is_file():
                raise RuleLoadError(schema_invalid, where, "family.yaml is missing")
            raw = path.read_bytes()
            try:
                family_file = parse_family_text(raw.decode("utf-8"))
            except UnicodeDecodeError as error:
                raise RuleLoadError(schema_invalid, where, "file is not UTF-8") from error
            if family_file.rule_family.family_id != name:
                raise RuleLoadError(
                    schema_invalid,
                    where,
                    f"directory {name} holds family {family_file.rule_family.family_id!r}",
                )
            sources.append(_Source(path, raw, family_file))
        return sources

    def _check_status(self, purpose: RunPurpose, sources: list[_Source]) -> None:
        allowed = _ALLOWED_STATUS[purpose]
        for source in sources:
            family = source.family_file.rule_family
            if family.status not in allowed:
                raise RuleLoadError(
                    RuleLoadErrorCode.status_not_allowed,
                    "rule_family.status",
                    f"{family.family_id} is {family.status.value}; "
                    f"run purpose {purpose.value} accepts {sorted(s.value for s in allowed)}",
                )

    def _check_knowledge_base_complete(self, active_sources: list[KbSource]) -> None:
        for source in sorted(active_sources, key=lambda row: row.id):
            for column in ("version_scope", "quality_note"):
                value = getattr(source, column)
                if value is None or not value.strip():
                    raise RuleLoadError(
                        RuleLoadErrorCode.kb_incomplete,
                        f"kb_sources.{source.id}.{column}",
                        "a holdout run needs every active source checked by the examiner",
                    )

    def _check_manifest(self, sources: list[_Source], kb_hash: str) -> None:
        def mismatch(path: str, detail: str) -> RuleLoadError:
            return RuleLoadError(RuleLoadErrorCode.manifest_mismatch, path, detail)

        try:
            manifest: Any = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except FileNotFoundError as error:
            raise mismatch("", f"{self.manifest_path.name} does not exist") from error
        except (OSError, ValueError) as error:  # unreadable, not UTF-8, not JSON
            raise mismatch("", f"{self.manifest_path.name} cannot be read: {error}") from error
        if not isinstance(manifest, dict):
            raise mismatch("", "the manifest is not a JSON object")
        rule_files = manifest.get("rule_files")
        if not isinstance(rule_files, dict):
            raise mismatch("rule_files", "missing or not an object")
        expected = {s.family_file.rule_family.family_id: s.content_hash for s in sources}
        if set(rule_files) != set(expected):
            raise mismatch(
                "rule_files",
                f"must list exactly {sorted(expected)}, lists {sorted(rule_files)}",
            )
        for family_id in sorted(expected):
            if rule_files[family_id] != expected[family_id]:
                raise mismatch(f"rule_files.{family_id}", "hash differs from the loaded file")
        if manifest.get("kb_sources") != kb_hash:
            raise mismatch("kb_sources", "hash differs from the loaded sources.yaml")

    def _store(self, source: _Source, validator: RuleValidator) -> LoadedFamily:
        family = source.family_file.rule_family
        content_hash = source.content_hash
        existing = self.db.scalars(
            select(RuleMetadata).where(
                RuleMetadata.family_id == family.family_id,
                RuleMetadata.content_hash == content_hash,
            )
        ).all()
        if existing:  # same bytes already stored: nothing is written
            row_ids = {row.profile_id: row.id for row in existing}
            return LoadedFamily(
                family.family_id,
                family.version,
                family.status.value,
                content_hash,
                row_ids,
                source.family_file,
            )

        relative = source.path.relative_to(self.rules_dir.parent).as_posix()
        now = datetime.now(UTC)

        def row(profile_id: str | None, **values: Any) -> RuleMetadata:
            return RuleMetadata(
                family_id=family.family_id,
                profile_id=profile_id,
                version=family.version,
                status=family.status.value,
                incident_scope=family.incident_scope,
                content_hash=content_hash,
                source_path=relative,
                loaded_at=now,
                **values,
            )

        rows: dict[str | None, RuleMetadata] = {None: row(None, applicability={}, claim_level=None)}
        for profile in family.profiles:
            rows[profile.profile_id] = row(
                profile.profile_id,
                applicability=profile.applicability.model_dump(mode="json"),
                claim_level=profile.claim_level.value,
            )
        self.db.add_all(rows.values())
        self.db.flush()

        for source_id in dict.fromkeys(family.reference_ids):
            self.db.add(RuleReference(rule_metadata_id=rows[None].id, source_id=source_id))
        for profile in family.profiles:
            cited = [i for c in _conditions(profile) for i in c.reference_ids or []]
            for source_id in dict.fromkeys(cited):
                self.db.add(
                    RuleReference(rule_metadata_id=rows[profile.profile_id].id, source_id=source_id)
                )
        for reference in validator.compile_references(source.family_file):
            owner = (
                None
                if reference.rule_element_key == family.family_id
                else (reference.rule_element_key.split(".", 1)[0])
            )
            self.db.add(
                RuleElementReference(
                    rule_metadata_id=rows[owner].id,
                    rule_element_key=reference.rule_element_key,
                    source_id=reference.source_id,
                    reference_role=reference.reference_role,
                    extracted_claim=reference.extracted_claim,
                    version_scope=reference.version_scope,
                    verification_status=reference.verification_status,
                )
            )
        self.db.flush()
        return LoadedFamily(
            family.family_id,
            family.version,
            family.status.value,
            content_hash,
            {profile_id: stored.id for profile_id, stored in rows.items()},
            source.family_file,
        )


def _conditions(profile: Any) -> list[Any]:
    return [
        condition
        for role in ("required", "optional", "contextual", "exclusionary")
        for condition in getattr(profile.conditions, role)
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Load the rule families into the database.")
    parser.add_argument("--run-purpose", default="authoring", choices=[p.value for p in RunPurpose])
    args = parser.parse_args(argv)

    from app.db.session import SessionLocal

    with SessionLocal() as db:
        try:
            rule_set = RuleLoader(db).load_all(args.run_purpose)
        except RuleLoadError as error:
            sys.stderr.write(f"rules not loaded: {error}\n")
            return 1
        db.commit()
    profiles = sum(len(family.row_ids) - 1 for family in rule_set.families)
    sys.stdout.write(
        f"loaded {len(rule_set.families)} families, {profiles} profiles "
        f"(rule_set_hash={rule_set.hash}, kb_hash={rule_set.kb_hash})\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
