import json
from pathlib import Path

import pytest

from src.exceptions import AgentError
from src.models import AgentState
from src.state.state_machine import AgentStateMachine


@pytest.fixture(autouse=True)
def _audit_to_tmp(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr("src.state.audit_logger.AUDIT_LOG", tmp_path / "audit.log")


def _records(tmp_path: Path) -> list[dict[str, object]]:
    text = (tmp_path / "audit.log").read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines()]


def test_happy_path_and_reconnect_cycle() -> None:
    machine = AgentStateMachine()
    assert machine.state == AgentState.starting
    for state in (
        AgentState.config_loaded,
        AgentState.adb_validated,
        AgentState.registered,
        AgentState.connected,
        AgentState.disconnected,
        AgentState.connected,
    ):
        machine.transition_to(state)
    assert machine.state == AgentState.connected


def test_cannot_skip_ahead(tmp_path: Path) -> None:
    machine = AgentStateMachine()
    with pytest.raises(AgentError):
        machine.transition_to("disconnected")
    assert machine.state == AgentState.starting
    rejected = _records(tmp_path)[0]
    assert rejected["event"] == "state_transition_rejected"


def test_unknown_state_is_rejected() -> None:
    with pytest.raises(AgentError):
        AgentStateMachine().transition_to("flying")


@pytest.mark.parametrize("state", [s for s in AgentState if s != AgentState.stopped])
def test_every_state_can_stop_and_stopped_is_final(state: AgentState) -> None:
    machine = AgentStateMachine()
    machine.state = state
    machine.transition_to(AgentState.stopped)
    assert machine.state == AgentState.stopped
    with pytest.raises(AgentError):
        machine.transition_to(AgentState.stopped)
    with pytest.raises(AgentError):
        machine.transition_to(AgentState.connected)
