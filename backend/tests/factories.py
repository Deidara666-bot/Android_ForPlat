"""Synthetic evidence chains for the rule engine tests (REF §ENGINE, v0.60.2).

One `Scene` is a case with a device and an agent. It builds, in the order the platform does:
acquisition session (+ operations with their parameters) -> evidence row of one part
(`operation_id`, `raw_source` from `app/core/raw_sources.py`, availability status) -> artifact
(parser version, parse status) -> normalized facts.

A fact has the shape the production normalizer gives it: the closed `NormalizedFact` model checks
the epistemic class, positive facts are `observed_true`, negative ones `observed_false`, a snapshot
is `current_state` with `event_time` NULL, and the context carries the keys the normalizer writes
(`user` for usage and activity, `source: apk_static` for bundle facts). A negative fact is tied to
the artifact that proves it, like the normalizer ties it.
"""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.constants import EvidenceState, TemporalSemantics
from app.models.acquisition_operation import AcquisitionOperation
from app.models.acquisition_session import AcquisitionSession
from app.models.agent import Agent
from app.models.artifact import Artifact
from app.models.case import Case
from app.models.device import Device
from app.models.evidence import Evidence
from app.models.normalized_event import NormalizedEvent
from app.models.user import User
from app.normalization.event_schema import EVENT_TYPE_CATALOG, NormalizedFact

T0 = datetime(2026, 10, 15, 8, 0, tzinfo=UTC)

# `object_type` per event type, as the normalizer writes it; event types no normalizer produces yet
# fall back to "record".
_OBJECT_TYPES = {
    "package_observed_installed": "package_name",
    "uid_observed": "uid",
    "apk_identity_observed": "apk_sha256",
    "apk_endpoint_reference_observed": "endpoint",
    "permission_observed_requested": "permission",
    "sensitive_communication_capability_observed_granted": "permission",
    "sensitive_communication_capability_observed_declared": "permission",
    "special_access_capability_observed_enabled": "special_access",
    "special_access_capability_observed_declared": "special_access",
    "accessibility_service_observed_declared": "component",
    "service_observed_declared": "component",
    "event_trigger_capability_observed_declared": "intent_action",
    "app_usage_observed": "usage_event",
    "activity_observed_resumed": "component",
    "process_observed_running": "process",
}


@dataclass(frozen=True)
class Part:
    """One acquired (or failed) part: its evidence row and its artifact, if it has one."""

    evidence: Evidence
    artifact: Artifact | None


class Scene:
    def __init__(self, session: Session, user: User, case_number: str = "C-FAC-1") -> None:
        self.session = session
        self.case = Case(case_number=case_number, title="synthetic", created_by=user.id)
        self.device = Device(
            serial="emulator-5554",
            manufacturer="Google",
            model="sdk",
            android_version="16",
            api_level=36,
            device_build="BUILD",
            last_seen_at=T0,
        )
        self.agent = Agent(agent_id=f"agent-{case_number}", version="0.1.0")
        session.add_all([self.case, self.device, self.agent])
        session.flush()
        self._sessions = 0

    def acquisition(
        self,
        operations: dict[str, dict[str, str]],
        *,
        timezone: str = "unknown",
        status: str = "completed",
    ) -> AcquisitionSession:
        """A session whose `operations` map operation ID -> parameters, newer than the last one."""
        self._sessions += 1
        row = AcquisitionSession(
            case_id=self.case.id,
            device_id=self.device.id,
            agent_id=self.agent.id,
            agent_version="0.1.0",
            android_version="16",
            api_level=36,
            device_build="BUILD",
            started_at=T0 + timedelta(minutes=self._sessions),
            timezone=timezone,
            status=status,
        )
        self.session.add(row)
        self.session.flush()
        for sequence, (operation, parameters) in enumerate(operations.items(), start=1):
            self.session.add(
                AcquisitionOperation(
                    session_id=row.id,
                    sequence=sequence,
                    operation_id=operation,
                    parameters=parameters,
                )
            )
        self.session.flush()
        return row

    def part(
        self,
        acquisition: AcquisitionSession,
        operation: str,
        raw_source: str,
        *,
        status: str = "acquired",
        parse: str | None = "parsed",
        parser_version: str = "1",
        artifact_type: str = "synthetic_entry",
        subject_key: str | None = None,
    ) -> Part:
        """Evidence of one part. An acquired part gets one artifact with the `parse` status
        (`None`: no artifact at all, i.e. not parsed yet); other statuses get no artifact."""
        evidence = Evidence(
            case_id=self.case.id,
            device_id=self.device.id,
            acquisition_session_id=acquisition.id,
            operation_id=operation,
            source_name=operation,
            raw_source=raw_source,
            acquired_at=acquisition.started_at,
            availability_status=status,
            availability_reason=None if status == "acquired" else "synthetic",
        )
        self.session.add(evidence)
        self.session.flush()
        artifact = None
        if status == "acquired" and parse is not None:
            artifact = self.artifact(
                evidence,
                parse,
                parser_version=parser_version,
                artifact_type=artifact_type,
                subject_key=subject_key,
            )
        return Part(evidence, artifact)

    def artifact(
        self,
        evidence: Evidence,
        parse: str = "parsed",
        *,
        parser_version: str = "1",
        artifact_type: str = "synthetic_entry",
        subject_key: str | None = None,
    ) -> Artifact:
        row = Artifact(
            evidence_id=evidence.id,
            artifact_type=artifact_type,
            parser_name="synthetic",
            parser_version=parser_version,
            subject_key=subject_key,
            raw_value="synthetic",
            parsed_value_json={"line_no": 1},
            parse_status=parse,
            parse_note="",
        )
        self.session.add(row)
        self.session.flush()
        return row

    def fact(
        self,
        artifact: Artifact,
        event_type: str,
        object_value: str,
        package: str | None,
        *,
        uid: int | None = None,
        positive: bool = True,
        static: bool = False,
        event_time: datetime | None = None,
        observed_at: datetime | None = None,
        **context: object,
    ) -> NormalizedEvent:
        """A fact of `event_type` about `package`; `positive=False` is an explicit negative fact."""
        historical = event_type == "app_usage_observed"
        base: dict[str, object] = {
            "artifact_type": artifact.artifact_type,
            "parser_name": artifact.parser_name,
            "parser_version": artifact.parser_version,
            "line_no": 1,
        }
        if event_type in ("app_usage_observed", "activity_observed_resumed"):
            base["user"] = 0
        if static:
            base["source"] = "apk_static"
        base.update(context)
        model = NormalizedFact(
            event_type=event_type,
            epistemic_class=EVENT_TYPE_CATALOG[event_type],
            subject_package=package,
            subject_uid=uid,
            object_type=_OBJECT_TYPES.get(event_type, "record"),
            object_value=object_value,
            predicate_value=positive,
            event_time=event_time,
            observed_at=observed_at or T0,
            window_start=None,
            window_end=None,
            temporal_semantics=(
                TemporalSemantics.historical_event
                if historical
                else TemporalSemantics.current_state
            ),
            evidence_state=EvidenceState.observed_true
            if positive
            else EvidenceState.observed_false,
            context_json=base,
        )
        row = NormalizedEvent(case_id=self.case.id, artifact_id=artifact.id, **model.model_dump())
        self.session.add(row)
        self.session.flush()
        return row

    def facts(self, artifact: Artifact, rows: list[tuple[Any, ...]]) -> list[NormalizedEvent]:
        """Several facts of one artifact: `(event_type, object_value, package[, kwargs])`."""
        made = []
        for row in rows:
            extra = row[3] if len(row) > 3 else {}
            made.append(self.fact(artifact, row[0], row[1], row[2], **extra))
        return made
