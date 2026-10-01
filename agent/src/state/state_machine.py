from src.exceptions import AgentError
from src.models import AgentState
from src.state.audit_logger import audit

_NEXT: dict[AgentState, frozenset[AgentState]] = {
    AgentState.starting: frozenset({AgentState.config_loaded}),
    AgentState.config_loaded: frozenset({AgentState.adb_validated}),
    AgentState.adb_validated: frozenset({AgentState.registered}),
    AgentState.registered: frozenset({AgentState.connected}),
    AgentState.connected: frozenset({AgentState.disconnected}),
    AgentState.disconnected: frozenset({AgentState.connected}),
    AgentState.stopped: frozenset(),
}


class AgentStateMachine:
    """starting -> config_loaded -> adb_validated -> registered -> connected <-> disconnected;
    every state may go to `stopped`, which is final."""

    def __init__(self) -> None:
        self.state = AgentState.starting

    def transition_to(self, target: AgentState | str) -> AgentState:
        try:
            new_state = AgentState(target)
        except ValueError:
            audit("state_transition_rejected", "unknown state", source=self.state, target=target)
            raise AgentError(f"unknown agent state {target!r}") from None
        allowed = new_state == AgentState.stopped and self.state != AgentState.stopped
        if not allowed and new_state not in _NEXT[self.state]:
            audit(
                "state_transition_rejected",
                "illegal transition",
                source=self.state,
                target=new_state,
            )
            raise AgentError(f"illegal transition {self.state.value} -> {new_state.value}")
        audit("state_changed", source=self.state, target=new_state)
        self.state = new_state
        return new_state
