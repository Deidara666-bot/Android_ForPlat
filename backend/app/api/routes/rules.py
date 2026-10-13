"""Read-only routes for the loaded rules and the knowledge base (REF section API2).

Everything shown is the *active* set: the rows that belong to the `RuleSet` loaded at startup
(`app.state.rule_set`) and the active knowledge-base sources. When the startup load failed there
is nothing to show: every route answers 503 with the error code.
"""

import uuid
from collections.abc import Iterable, Sequence
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.kb_source import KbSource
from app.models.rule_metadata import RuleElementReference, RuleMetadata
from app.research.rules.loader import LoadedFamily, RuleSet
from app.research.rules.schema import RuleCondition, RuleProfile
from app.schemas.rules import (
    ConditionOut,
    FamilyDetailOut,
    FamilySummaryOut,
    KbSourceOut,
    OutputOut,
    ProfileDetailOut,
    ProfileSummaryOut,
    ReferenceOut,
)

router = APIRouter(tags=["rules"], dependencies=[Depends(get_current_user)])

_ROLES = ("required", "optional", "contextual", "exclusionary")
_UNAVAILABLE: dict[int | str, dict[str, Any]] = {
    503: {"description": "Rules were not loaded at startup; body is `{code}`"}
}


def _unavailable(request: Request) -> JSONResponse | None:
    """503 `{code}` when there is no loaded rule set (failed or not attempted), else None."""
    if getattr(request.app.state, "rule_set", None) is not None:
        return None
    health = getattr(request.app.state, "rules_status", None)
    return JSONResponse(status_code=503, content={"code": health.code if health else None})


def _rule_set(request: Request) -> RuleSet:
    rule_set = request.app.state.rule_set
    assert isinstance(rule_set, RuleSet)
    return rule_set


def _row_ids(families: Iterable[LoadedFamily]) -> set[uuid.UUID]:
    return {row_id for family in families for row_id in family.row_ids.values()}


def _rows(db: Session, families: Iterable[LoadedFamily]) -> dict[uuid.UUID, RuleMetadata]:
    ids = _row_ids(families)
    return {row.id: row for row in db.scalars(select(RuleMetadata).where(RuleMetadata.id.in_(ids)))}


@router.get(
    "/rules",
    response_model=list[FamilySummaryOut],
    responses=_UNAVAILABLE,
    summary="Loaded rule families and their profiles (active rows only)",
)
def list_rules(
    request: Request, db: Annotated[Session, Depends(get_db)]
) -> list[FamilySummaryOut] | JSONResponse:
    if (refusal := _unavailable(request)) is not None:
        return refusal
    families = _rule_set(request).families
    rows = _rows(db, families)
    result = []
    for family in families:
        head = rows[family.row_ids[None]]
        profiles = []
        for profile in family.family_file.rule_family.profiles:
            row = rows[family.row_ids[profile.profile_id]]
            profiles.append(
                ProfileSummaryOut(
                    profile_id=profile.profile_id,
                    version=row.version,
                    status=row.status,
                    claim_level=row.claim_level,
                    applicability=row.applicability,
                )
            )
        result.append(
            FamilySummaryOut(
                family_id=family.family_id,
                version=head.version,
                status=head.status,
                profiles=profiles,
            )
        )
    return result


@router.get(
    "/rules/{family_id}",
    response_model=FamilyDetailOut,
    responses={**_UNAVAILABLE, 404: {"description": "Unknown family"}},
    summary="One family: profiles, conditions (from the parsed YAML) and cited sources",
)
def get_rule_family(
    family_id: str, request: Request, db: Annotated[Session, Depends(get_db)]
) -> FamilyDetailOut | JSONResponse:
    if (refusal := _unavailable(request)) is not None:
        return refusal
    family = next((f for f in _rule_set(request).families if f.family_id == family_id), None)
    if family is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="keluarga aturan tidak ditemukan")
    rows = _rows(db, [family])
    cited = {
        (reference.rule_element_key, reference.source_id): reference
        for reference in db.scalars(
            select(RuleElementReference).where(
                RuleElementReference.rule_metadata_id.in_(_row_ids([family]))
            )
        )
    }

    def references(key: str, source_ids: Sequence[str] | None) -> list[ReferenceOut]:
        # YAML order; role, claim and verification come from the stored element reference
        return [
            ReferenceOut(
                source_id=source_id,
                reference_role=cited[key, source_id].reference_role,
                extracted_claim=cited[key, source_id].extracted_claim,
                version_scope=cited[key, source_id].version_scope,
                verification_status=cited[key, source_id].verification_status,
            )
            for source_id in source_ids or []
        ]

    def condition(profile: RuleProfile, item: RuleCondition) -> ConditionOut:
        return ConditionOut(
            condition_id=item.condition_id,
            fact=item.fact,
            source_group=item.source_group.value,
            expects_epistemic_class=item.expects_epistemic_class.value,
            operator=item.operator.value,
            field=item.field,
            value=item.value,
            values=item.values,
            references=references(f"{profile.profile_id}.{item.condition_id}", item.reference_ids),
        )

    parsed = family.family_file.rule_family
    profiles = []
    for profile in parsed.profiles:
        row = rows[family.row_ids[profile.profile_id]]
        profiles.append(
            ProfileDetailOut(
                profile_id=profile.profile_id,
                name=profile.name,
                version=row.version,
                status=row.status,
                claim_level=profile.claim_level.value,
                applicability=row.applicability,
                subject_binding=list(profile.subject_binding),
                time_binding=profile.time_binding.value,
                validation_only=profile.validation_only,
                conditions={
                    role: [condition(profile, item) for item in getattr(profile.conditions, role)]
                    for role in _ROLES
                },
                output=OutputOut(
                    behavior_id=profile.output.behavior_id,
                    summary_template=profile.output.summary_template,
                    limitations=list(profile.output.limitations),
                ),
            )
        )
    head = rows[family.row_ids[None]]
    return FamilyDetailOut(
        family_id=family.family_id,
        version=head.version,
        status=head.status,
        incident_scope=head.incident_scope,
        references=references(family.family_id, parsed.reference_ids),
        profiles=profiles,
    )


@router.get(
    "/kb/sources",
    response_model=list[KbSourceOut],
    responses=_UNAVAILABLE,
    summary="Active knowledge-base sources",
)
def list_kb_sources(
    request: Request, db: Annotated[Session, Depends(get_db)]
) -> list[KbSourceOut] | JSONResponse:
    if (refusal := _unavailable(request)) is not None:
        return refusal
    sources = db.scalars(select(KbSource).where(KbSource.active.is_(True)).order_by(KbSource.id))
    return [
        KbSourceOut(
            id=source.id,
            title=source.title,
            publisher=source.publisher,
            url=source.url,
            accessed_at=source.accessed_at,
            extracted_claim=source.extracted_claim,
            version_scope=source.version_scope,
            reference_role=source.reference_role,
            quality_note=source.quality_note,
            verification_status=source.verification_status,
        )
        for source in sources
    ]
