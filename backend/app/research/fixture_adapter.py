"""Validation fixtures for the rule engine (REF §ENGINE "Run", 02_ARSITEKTUR §Z.0.3).

To prove that an exclusionary condition constrains a profile, a test needs a profile that has one.
The production YAML has none that production can reach, so the adapter clones a target profile
**in memory** and adds the exclusionary condition `synthetic_exclusion_marker_observed`. Nothing
here touches the database or the YAML files: the clone is never stored, never loaded by the rule
loader, and never listed by the API.

Only the runs that exist to validate the rules may use it (`authoring`, `holdout`). The marker
fact itself comes from a test factory, never from the normalizer (it has no producer).
"""

from app.core.constants import EpistemicClass, Operator, RunPurpose, SourceGroup
from app.research.rules.schema import RuleCondition, RuleProfile

MARKER_FACT = "synthetic_exclusion_marker_observed"
MARKER_CONDITION_ID = "FX01"
FIXTURE_RUN_PURPOSES = frozenset({RunPurpose.authoring, RunPurpose.holdout})


class FixtureNotAllowedError(ValueError):
    """A validation fixture was asked for a run that is not a validation run."""


def with_exclusion_marker(profile: RuleProfile, run_purpose: RunPurpose) -> RuleProfile:
    """A copy of `profile` with the marker as an exclusionary condition, `validation_only`.

    The clone has its own `profile_id` (`<id>-FIXTURE`) and applies only to the validation run
    purposes the original lists, so it can never be evaluated for `production`.
    """
    if run_purpose not in FIXTURE_RUN_PURPOSES:
        raise FixtureNotAllowedError(
            f"validation fixtures are only for {sorted(p.value for p in FIXTURE_RUN_PURPOSES)}, "
            f"not {run_purpose.value!r}"
        )
    if any(c.fact == MARKER_FACT for c in profile.conditions.exclusionary):
        raise ValueError(f"profile {profile.profile_id} already has the exclusion marker")
    marker = RuleCondition(
        condition_id=MARKER_CONDITION_ID,
        fact=MARKER_FACT,
        source_group=SourceGroup.APP_SYSTEM_STATE,
        expects_epistemic_class=EpistemicClass.identity_attribute,
        operator=Operator.exists,
    )
    data = profile.model_dump(mode="python")
    data["profile_id"] = f"{profile.profile_id}-FIXTURE"
    data["name"] = f"{profile.name} (validation fixture)"
    data["validation_only"] = True
    validation_purposes = [
        purpose
        for purpose in data["applicability"]["run_purposes"]
        if purpose in FIXTURE_RUN_PURPOSES
    ]
    if not validation_purposes:
        raise ValueError(f"profile {profile.profile_id} applies to no validation run purpose")
    data["applicability"]["run_purposes"] = validation_purposes
    data["conditions"]["exclusionary"] = [
        *data["conditions"]["exclusionary"],
        marker.model_dump(mode="python"),
    ]
    return RuleProfile.model_validate(data)
