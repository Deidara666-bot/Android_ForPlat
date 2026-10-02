from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any

from app.core.constants import AvailabilityStatus, EvidenceState, ParseStatus
from app.normalization.event_schema import NormalizedFact
from app.normalization.subject_resolution import (
    INVENTORY_ARTIFACT_TYPE,
    ArtifactLike,
    subject_from_inventory,
)
from app.normalization.temporal import current_state_times

_METADATA_ARTIFACT_TYPE = "device_build_property"


class UnsupportedArtifactTypeError(ValueError):
    pass


def split_claims(
    base: Mapping[str, Any], claims: Sequence[tuple[str, str, str]]
) -> list[NormalizedFact]:
    """One claim (event_type, object_type, object_value) becomes exactly one fact."""
    return [
        NormalizedFact(
            **base, event_type=event_type, object_type=object_type, object_value=object_value
        )
        for event_type, object_type, object_value in claims
    ]


def normalize(
    artifact: ArtifactLike,
    *,
    observed_at: datetime,
    availability_status: AvailabilityStatus | str,
) -> list[NormalizedFact]:
    if AvailabilityStatus(availability_status) != AvailabilityStatus.acquired:
        return []
    if ParseStatus(artifact.parse_status) != ParseStatus.parsed:
        return []
    if artifact.artifact_type == _METADATA_ARTIFACT_TYPE:
        return []
    if artifact.artifact_type != INVENTORY_ARTIFACT_TYPE:
        raise UnsupportedArtifactTypeError(artifact.artifact_type)

    package, uid = subject_from_inventory(artifact)
    base: dict[str, Any] = {
        "subject_package": package,
        "subject_uid": uid,
        "predicate_value": True,
        "evidence_state": EvidenceState.observed_true,
        "context_json": {
            "artifact_type": artifact.artifact_type,
            "parser_name": artifact.parser_name,
            "parser_version": artifact.parser_version,
            "line_no": artifact.parsed_value_json.get("line_no"),
        },
        **current_state_times(observed_at),
    }
    return split_claims(
        base,
        [
            ("package_observed_installed", "package_name", package),
            ("uid_observed", "uid", str(uid)),
        ],
    )
