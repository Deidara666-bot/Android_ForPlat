from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.kb_source import KbSource
from app.models.rule_metadata import RuleElementReference, RuleMetadata, RuleReference
from app.research.knowledge_base.loader import KnowledgeBaseLoader


def _rule(**overrides: object) -> RuleMetadata:
    values: dict[str, object] = {
        "family_id": "APKF-K01",
        "profile_id": None,
        "version": 1,
        "status": "design_baseline",
        "applicability": {},
        "claim_level": None,
        "incident_scope": "apk_fraud_investigation",
        "content_hash": "0" * 64,
        "source_path": "apk_fraud/APKF-K01/family.yaml",
        "loaded_at": datetime(2026, 10, 13, tzinfo=UTC),
    }
    return RuleMetadata(**{**values, **overrides})


def test_a_family_row_and_a_profile_row_with_their_references_are_stored(session: Session) -> None:
    KnowledgeBaseLoader().load_to_db(session)
    family = _rule()
    profile = _rule(
        profile_id="APKF-K01-P01",
        claim_level="capability",
        applicability={"evidence_modes": ["installed_runtime"], "run_purposes": ["authoring"]},
    )
    session.add_all([family, profile])
    session.flush()
    session.add_all(
        [
            RuleReference(rule_metadata_id=family.id, source_id="KB-AND-PACKAGE"),
            RuleElementReference(
                rule_metadata_id=profile.id,
                rule_element_key="APKF-K01-P01.C01",
                source_id="KB-AND-PACKAGE",
                reference_role="artifact_semantics",
                extracted_claim="identitas package terpasang",
                version_scope=None,
                verification_status="verified_design",
            ),
        ]
    )
    session.flush()
    assert family.profile_id is None and family.claim_level is None
    assert profile.claim_level == "capability"


def test_a_reference_to_an_unknown_source_is_refused(session: Session) -> None:
    family = _rule()
    session.add(family)
    session.flush()
    session.add(RuleReference(rule_metadata_id=family.id, source_id="KB-DOES-NOT-EXIST"))
    with pytest.raises(IntegrityError, match="fk_rule_references_source_id_kb_sources"):
        session.flush()


@pytest.mark.parametrize(
    ("overrides", "constraint"),
    [
        ({"status": "production_ready"}, "ck_rule_metadata_status"),
        ({"claim_level": "proven"}, "ck_rule_metadata_claim_level"),
    ],
)
def test_the_database_rejects_values_outside_the_closed_enums(
    session: Session, overrides: dict[str, object], constraint: str
) -> None:
    session.add(_rule(**overrides))
    with pytest.raises(IntegrityError, match=constraint):
        session.flush()


def test_an_element_reference_needs_a_known_role(session: Session) -> None:
    session.add(
        KbSource(
            id="KB-X",
            title="t",
            publisher="p",
            url="https://x",
            accessed_at=datetime(2026, 9, 5, tzinfo=UTC).date(),
            extracted_claim="c",
            reference_role="artifact_semantics",
            verification_status="verified_design",
        )
    )
    rule = _rule()
    session.add(rule)
    session.flush()
    session.add(
        RuleElementReference(
            rule_metadata_id=rule.id,
            rule_element_key="APKF-K01",
            source_id="KB-X",
            reference_role="evidence_score",
            extracted_claim="c",
            verification_status="verified_design",
        )
    )
    with pytest.raises(IntegrityError, match="ck_rule_element_references_reference_role"):
        session.flush()
