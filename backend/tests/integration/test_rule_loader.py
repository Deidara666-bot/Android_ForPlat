"""Loading rules into `rule_metadata`, with the status/KB/manifest gate (v0.50.4)."""

import hashlib
import json
import shutil
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.rule_metadata import RuleElementReference, RuleMetadata, RuleReference
from app.research.knowledge_base.loader import SOURCES_PATH, KnowledgeBaseLoader
from app.research.rules.errors import RuleLoadError, RuleLoadErrorCode
from app.research.rules.loader import RULES_DIR, RuleLoader, combine_hashes

_FAMILIES = ["APKF-K01", "APKF-K02", "APKF-K03", "APKF-K04", "APKF-K05"]
_OPEN = "null  # TODO(open-data)"


def _count(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rules_copy(tmp_path: Path, status: str | None = None, name: str = "apk_fraud") -> Path:
    """The five real YAML files under `tmp_path/<name>`, family status optionally rewritten."""
    target = tmp_path / name
    for family in _FAMILIES:
        folder = target / family
        folder.mkdir(parents=True)
        text = (RULES_DIR / family / "family.yaml").read_text(encoding="utf-8")
        if status is not None:
            assert text.count("  status: design_baseline\n") == 1
            text = text.replace("  status: design_baseline\n", f"  status: {status}\n")
        (folder / "family.yaml").write_text(text, encoding="utf-8", newline="\n")
    return target


def _complete_sources(tmp_path: Path) -> Path:
    """`sources.yaml` with both open-data columns filled in (a synthetic, checked KB)."""
    text = SOURCES_PATH.read_text(encoding="utf-8")
    assert text.count(_OPEN) == 22
    text = text.replace(f"version_scope: {_OPEN}", 'version_scope: "API 36"')
    text = text.replace(f"quality_note: {_OPEN}", 'quality_note: "checked"')
    path = tmp_path / "sources.yaml"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _manifest(
    tmp_path: Path, rules: Path, sources: Path, *, drop: str | None = None, **changes: object
) -> Path:
    document: dict[str, object] = {
        "rule_files": {f: _sha(rules / f / "family.yaml") for f in _FAMILIES},
        "kb_sources": _sha(sources),
        "other_key_the_loader_ignores": [1, 2, 3],
    }
    document.update(changes)
    if drop:
        del document[drop]
    path = tmp_path / "freeze_manifest.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


@pytest.fixture
def kb(session: Session) -> None:
    KnowledgeBaseLoader().load_to_db(session)


def _error(session: Session, purpose: str, **kwargs: object) -> RuleLoadError:
    with pytest.raises(RuleLoadError) as caught:
        RuleLoader(session, **kwargs).load_all(purpose)  # type: ignore[arg-type]
    return caught.value


@pytest.mark.usefixtures("kb")
def test_authoring_loads_five_families_and_sixteen_profiles(session: Session) -> None:
    rule_set = RuleLoader(session).load_all("authoring")

    assert [f.family_id for f in rule_set.families] == _FAMILIES
    assert _count(session, RuleMetadata) == 21
    profiles = session.scalar(select(func.count()).where(RuleMetadata.profile_id.is_not(None)))
    assert profiles == 16
    for family in rule_set.families:
        assert family.content_hash == _sha(RULES_DIR / family.family_id / "family.yaml")
        assert None in family.row_ids  # the family row
    first = session.get(RuleMetadata, rule_set.families[0].row_ids["APKF-K01-P01"])
    assert first is not None and first.claim_level == "capability"
    assert first.source_path == "apk_fraud/APKF-K01/family.yaml"
    assert first.applicability == {
        "evidence_modes": ["installed_runtime"],
        "run_purposes": ["authoring", "holdout", "benign_control", "production"],
    }
    family_row = session.get(RuleMetadata, rule_set.families[0].row_ids[None])
    assert family_row is not None and family_row.applicability == {}
    assert family_row.claim_level is None


@pytest.mark.usefixtures("kb")
def test_loading_twice_writes_nothing_new_and_gives_the_same_hashes(session: Session) -> None:
    loader = RuleLoader(session)
    first = loader.load_all("authoring")
    counts = (
        _count(session, RuleMetadata),
        _count(session, RuleReference),
        _count(session, RuleElementReference),
    )
    second = loader.load_all("benign_control")

    assert (
        _count(session, RuleMetadata),
        _count(session, RuleReference),
        _count(session, RuleElementReference),
    ) == counts
    assert second.hash == first.hash and second.kb_hash == first.kb_hash
    assert [f.row_ids for f in second.families] == [f.row_ids for f in first.families]


@pytest.mark.usefixtures("kb")
def test_references_are_written_for_family_profile_and_condition(session: Session) -> None:
    rule_set = RuleLoader(session).load_all("authoring")
    k01 = rule_set.families[0]
    family_links = session.scalars(
        select(RuleReference.source_id).where(RuleReference.rule_metadata_id == k01.row_ids[None])
    ).all()
    assert sorted(family_links) == ["KB-AND-PACKAGE", "KB-AND-PERMISSION", "KB-MITRE-T1644"]
    profile_links = session.scalars(
        select(RuleReference.source_id).where(
            RuleReference.rule_metadata_id == k01.row_ids["APKF-K01-P01"]
        )
    ).all()
    assert sorted(profile_links) == ["KB-AND-PACKAGE", "KB-AND-PERMISSION", "KB-MITRE-T1644"]
    element = session.scalars(
        select(RuleElementReference).where(
            RuleElementReference.rule_element_key == "APKF-K01-P01.C02",
            RuleElementReference.source_id == "KB-MITRE-T1644",
        )
    ).one()
    assert element.rule_metadata_id == k01.row_ids["APKF-K01-P01"]
    assert element.reference_role == "technique_mapping"
    assert element.version_scope is None  # open data stays null
    keys = set(session.scalars(select(RuleElementReference.rule_element_key)))
    assert "APKF-K01" in keys


@pytest.mark.usefixtures("kb")
def test_a_changed_file_adds_rows_and_leaves_the_old_version(
    session: Session, tmp_path: Path
) -> None:
    original = RuleLoader(session).load_all("authoring")
    rules = _rules_copy(tmp_path)
    k01 = rules / "APKF-K01" / "family.yaml"
    k01.write_text(k01.read_text(encoding="utf-8").replace("  version: 1\n", "  version: 2\n", 1))

    updated = RuleLoader(session, rules_dir=rules).load_all("authoring")

    assert _count(session, RuleMetadata) == 21 + 4  # K01 family row + its 3 profiles, again
    assert updated.hash != original.hash
    old, new = original.families[0], updated.families[0]
    assert old.content_hash != new.content_hash and new.version == 2
    assert set(old.row_ids.values()).isdisjoint(new.row_ids.values())
    for before, after in zip(original.families[1:], updated.families[1:], strict=True):
        assert before.row_ids == after.row_ids  # untouched families keep their active rows
    assert session.get(RuleMetadata, old.row_ids[None]) is not None  # the old version stays


def test_the_rule_set_hash_is_fixed_by_the_family_hashes() -> None:
    hashes = {"APKF-K02": "b" * 64, "APKF-K01": "a" * 64}
    assert combine_hashes(hashes) == combine_hashes(dict(reversed(hashes.items())))
    assert combine_hashes(hashes) != combine_hashes({**hashes, "APKF-K02": "c" * 64})


def test_the_knowledge_base_hash_is_the_sha256_of_sources_yaml() -> None:
    assert KnowledgeBaseLoader().content_hash() == _sha(SOURCES_PATH)


@pytest.mark.usefixtures("kb")
def test_holdout_refuses_the_design_baseline_and_writes_nothing(session: Session) -> None:
    error = _error(session, "holdout")
    assert error.code == "status_not_allowed"
    assert _count(session, RuleMetadata) == 0


@pytest.mark.usefixtures("kb")
def test_production_refuses_the_design_baseline_but_takes_a_candidate(
    session: Session, tmp_path: Path
) -> None:
    assert _error(session, "production").code == "status_not_allowed"
    candidate = _rules_copy(tmp_path, "authoring_candidate")
    rule_set = RuleLoader(session, rules_dir=candidate).load_all("production")
    assert {f.status for f in rule_set.families} == {"authoring_candidate"}


@pytest.mark.usefixtures("kb")
def test_authoring_refuses_a_frozen_file(session: Session, tmp_path: Path) -> None:
    frozen = _rules_copy(tmp_path, "frozen_for_holdout")
    assert _error(session, "authoring", rules_dir=frozen).code == "status_not_allowed"


@pytest.mark.usefixtures("kb")
def test_a_frozen_file_with_an_unchecked_knowledge_base_is_kb_incomplete(
    session: Session, tmp_path: Path
) -> None:
    frozen = _rules_copy(tmp_path, "frozen_for_holdout")
    error = _error(session, "holdout", rules_dir=frozen)
    assert error.code == "kb_incomplete"
    assert error.path == "kb_sources.KB-AND-ACCESSIBILITY.version_scope"
    assert _count(session, RuleMetadata) == 0


@pytest.fixture
def frozen_world(session: Session, tmp_path: Path) -> tuple[Path, Path]:
    """Frozen synthetic rules + a fully checked synthetic knowledge base in the test DB."""
    rules = _rules_copy(tmp_path, "frozen_for_holdout")
    sources = _complete_sources(tmp_path)
    KnowledgeBaseLoader(sources).load_to_db(session)
    return rules, sources


def _holdout(session: Session, rules: Path, sources: Path, manifest: Path) -> RuleLoadError:
    return _error(session, "holdout", rules_dir=rules, sources_path=sources, manifest_path=manifest)


def test_a_matching_manifest_lets_a_holdout_run_through(
    session: Session, tmp_path: Path, frozen_world: tuple[Path, Path]
) -> None:
    rules, sources = frozen_world
    manifest = _manifest(tmp_path, rules, sources)
    rule_set = RuleLoader(
        session, rules_dir=rules, sources_path=sources, manifest_path=manifest
    ).load_all("holdout")
    assert rule_set.run_purpose == "holdout"
    assert rule_set.kb_hash == _sha(sources)
    assert _count(session, RuleMetadata) == 21


def test_a_missing_manifest_is_a_mismatch(
    session: Session, tmp_path: Path, frozen_world: tuple[Path, Path]
) -> None:
    rules, sources = frozen_world
    error = _holdout(session, rules, sources, tmp_path / "absent.json")
    assert error.code == "manifest_mismatch"
    assert _count(session, RuleMetadata) == 0


def test_an_unreadable_manifest_is_a_mismatch(
    session: Session, tmp_path: Path, frozen_world: tuple[Path, Path]
) -> None:
    rules, sources = frozen_world
    broken = tmp_path / "freeze_manifest.json"
    for text in ("{not json", "[]", '"text"'):
        broken.write_text(text, encoding="utf-8")
        assert _holdout(session, rules, sources, broken).code == "manifest_mismatch"


def test_one_family_hash_that_differs_is_a_mismatch(
    session: Session, tmp_path: Path, frozen_world: tuple[Path, Path]
) -> None:
    rules, sources = frozen_world
    wrong = {f: _sha(rules / f / "family.yaml") for f in _FAMILIES}
    wrong["APKF-K03"] = "0" * 64
    error = _holdout(session, rules, sources, _manifest(tmp_path, rules, sources, rule_files=wrong))
    assert (error.code, error.path) == ("manifest_mismatch", "rule_files.APKF-K03")


def test_a_knowledge_base_hash_that_differs_is_a_mismatch(
    session: Session, tmp_path: Path, frozen_world: tuple[Path, Path]
) -> None:
    rules, sources = frozen_world
    error = _holdout(
        session, rules, sources, _manifest(tmp_path, rules, sources, kb_sources="f" * 64)
    )
    assert (error.code, error.path) == ("manifest_mismatch", "kb_sources")


@pytest.mark.parametrize("dropped", ["APKF-K05", None])
def test_the_manifest_must_list_exactly_the_five_families(
    session: Session, tmp_path: Path, frozen_world: tuple[Path, Path], dropped: str | None
) -> None:
    rules, sources = frozen_world
    listed = {f: _sha(rules / f / "family.yaml") for f in _FAMILIES}
    if dropped:
        del listed[dropped]  # one family short
    else:
        listed["APKF-K06"] = "1" * 64  # one family too many
    error = _holdout(
        session, rules, sources, _manifest(tmp_path, rules, sources, rule_files=listed)
    )
    assert (error.code, error.path) == ("manifest_mismatch", "rule_files")


@pytest.mark.parametrize("missing", ["rule_files", "kb_sources"])
def test_a_manifest_without_a_required_key_is_a_mismatch(
    session: Session, tmp_path: Path, frozen_world: tuple[Path, Path], missing: str
) -> None:
    rules, sources = frozen_world
    error = _holdout(session, rules, sources, _manifest(tmp_path, rules, sources, drop=missing))
    assert error.code == "manifest_mismatch" and error.path == missing


@pytest.mark.usefixtures("kb")
def test_the_gate_order_is_status_then_knowledge_base_then_manifest(
    session: Session, tmp_path: Path
) -> None:
    absent = tmp_path / "absent.json"
    # design_baseline + unchecked KB + no manifest: the status is reported first
    assert _error(session, "holdout", manifest_path=absent).code == "status_not_allowed"
    # frozen + unchecked KB + no manifest: the knowledge base is reported next
    frozen = _rules_copy(tmp_path, "frozen_for_holdout")
    assert (
        _error(session, "holdout", rules_dir=frozen, manifest_path=absent).code == "kb_incomplete"
    )


@pytest.mark.usefixtures("kb")
def test_a_file_that_breaks_the_contract_writes_nothing(session: Session, tmp_path: Path) -> None:
    rules = _rules_copy(tmp_path)
    k02 = rules / "APKF-K02" / "family.yaml"
    k02.write_text(
        k02.read_text(encoding="utf-8").replace("fact: package_observed_installed", "fact: nope", 1)
    )
    error = _error(session, "authoring", rules_dir=rules)
    assert error.code == RuleLoadErrorCode.unknown_fact
    assert _count(session, RuleMetadata) == 0


def test_an_unknown_run_purpose_is_refused(session: Session) -> None:
    with pytest.raises(ValueError, match="run_purpose|RunPurpose|not a valid"):
        RuleLoader(session).load_all("demo")


def test_rules_without_a_loaded_knowledge_base_do_not_resolve(session: Session) -> None:
    assert _error(session, "authoring").code == "reference_unresolved"
    assert _count(session, RuleMetadata) == 0


# --- the closed family set (R1) ---------------------------------------------------------


@pytest.mark.usefixtures("kb")
@pytest.mark.parametrize("purpose", ["authoring", "benign_control", "holdout", "production"])
def test_an_empty_rules_folder_is_schema_invalid_for_every_purpose(
    session: Session, tmp_path: Path, purpose: str
) -> None:
    empty = tmp_path / "apk_fraud"
    empty.mkdir()
    error = _error(session, purpose, rules_dir=empty)
    assert (error.code, error.path) == ("schema_invalid", "APKF-K01")
    assert _count(session, RuleMetadata) == 0


@pytest.mark.usefixtures("kb")
def test_a_missing_rules_folder_is_schema_invalid(session: Session, tmp_path: Path) -> None:
    assert _error(session, "authoring", rules_dir=tmp_path / "absent").code == "schema_invalid"


@pytest.mark.usefixtures("kb")
@pytest.mark.parametrize("purpose", ["authoring", "production", "holdout"])
def test_a_missing_family_directory_is_schema_invalid(
    session: Session, tmp_path: Path, purpose: str
) -> None:
    rules = _rules_copy(tmp_path, "frozen_for_holdout")
    shutil.rmtree(rules / "APKF-K05")
    error = _error(session, purpose, rules_dir=rules)
    assert (error.code, error.path) == ("schema_invalid", "APKF-K05")
    assert _count(session, RuleMetadata) == 0


@pytest.mark.usefixtures("kb")
def test_a_sixth_directory_is_schema_invalid(session: Session, tmp_path: Path) -> None:
    rules = _rules_copy(tmp_path)
    shutil.copytree(rules / "APKF-K01", rules / "APKF-K06")
    error = _error(session, "authoring", rules_dir=rules)
    assert (error.code, error.path) == ("schema_invalid", "APKF-K06")


@pytest.mark.usefixtures("kb")
def test_a_directory_holding_another_family_is_schema_invalid(
    session: Session, tmp_path: Path
) -> None:
    rules = _rules_copy(tmp_path)
    k01 = rules / "APKF-K01" / "family.yaml"
    text = k01.read_text(encoding="utf-8")
    marker = "  family_id: APKF-K01" + chr(10)
    assert text.count(marker) == 1
    k01.write_text(text.replace(marker, "  family_id: APKF-K02" + chr(10)))
    error = _error(session, "authoring", rules_dir=rules)
    assert (error.code, error.path) == ("schema_invalid", "APKF-K01/family.yaml")
    assert "APKF-K02" in error.detail
    assert _count(session, RuleMetadata) == 0


@pytest.mark.usefixtures("kb")
def test_a_family_directory_without_its_file_is_schema_invalid(
    session: Session, tmp_path: Path
) -> None:
    rules = _rules_copy(tmp_path)
    (rules / "APKF-K03" / "family.yaml").unlink()
    error = _error(session, "authoring", rules_dir=rules)
    assert (error.code, error.path) == ("schema_invalid", "APKF-K03/family.yaml")


# --- two ways to load (R2) --------------------------------------------------------------


def test_load_all_needs_a_run_purpose(session: Session) -> None:
    with pytest.raises(ValueError, match="run_purpose is required"):
        RuleLoader(session).load_all(None)  # type: ignore[arg-type]
    assert _count(session, RuleMetadata) == 0


@pytest.mark.usefixtures("kb")
def test_load_validated_skips_the_gate_for_frozen_rules_and_an_unchecked_kb(
    session: Session, tmp_path: Path
) -> None:
    frozen = _rules_copy(tmp_path, "frozen_for_holdout")
    # load_all("holdout") on the same input is refused (unchecked KB, no manifest) ...
    assert _error(session, "holdout", rules_dir=frozen).code == "kb_incomplete"
    # ... load_validated has no run purpose, so no gate
    rule_set = RuleLoader(session, rules_dir=frozen).load_validated()
    assert rule_set.run_purpose is None
    assert {f.status for f in rule_set.families} == {"frozen_for_holdout"}
    assert _count(session, RuleMetadata) == 21


@pytest.mark.usefixtures("kb")
def test_load_validated_and_load_all_share_rows_and_hashes(session: Session) -> None:
    loader = RuleLoader(session)
    validated = loader.load_validated()
    counts = _count(session, RuleMetadata), _count(session, RuleElementReference)
    gated = loader.load_all("authoring")
    assert (_count(session, RuleMetadata), _count(session, RuleElementReference)) == counts
    assert (gated.hash, gated.kb_hash) == (validated.hash, validated.kb_hash)
    assert gated.run_purpose == "authoring" and validated.run_purpose is None


@pytest.mark.usefixtures("kb")
def test_load_validated_still_validates(session: Session, tmp_path: Path) -> None:
    rules = _rules_copy(tmp_path)
    k02 = rules / "APKF-K02" / "family.yaml"
    k02.write_text(
        k02.read_text(encoding="utf-8").replace("fact: package_observed_installed", "fact: nope", 1)
    )
    with pytest.raises(RuleLoadError) as caught:
        RuleLoader(session, rules_dir=rules).load_validated()
    assert caught.value.code == RuleLoadErrorCode.unknown_fact
    assert _count(session, RuleMetadata) == 0


def test_load_validated_without_a_knowledge_base_does_not_resolve(session: Session) -> None:
    with pytest.raises(RuleLoadError) as caught:
        RuleLoader(session).load_validated()
    assert caught.value.code == "reference_unresolved"
