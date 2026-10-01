import argparse
import asyncio
import logging
import sys

from src.config import get_settings
from src.device.adb_controller import adb_version
from src.exceptions import AgentError
from src.logging_config import configure_logging
from src.models import AgentState
from src.state.audit_logger import audit
from src.state.state_machine import AgentStateMachine
from src.transport.api_client import ApiClient
from src.transport.ws_client import run_forever

log = logging.getLogger("agent")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Android ForPlat agent")
    parser.add_argument("--once", action="store_true", help="stop once the agent is ready")
    args = parser.parse_args(argv)

    configure_logging()
    logging.getLogger("httpx").setLevel(logging.WARNING)

    machine = AgentStateMachine()
    try:
        settings = get_settings()
        log.info(
            "config loaded: agent_id=%s backend=%s", settings.agent_id, settings.backend_base_url
        )
        audit("config_loaded", agent_id=settings.agent_id)
        machine.transition_to(AgentState.config_loaded)

        version = adb_version(settings.adb_path)
        log.info("adb version: %s", version)
        audit("adb_validated", adb=version)
        machine.transition_to(AgentState.adb_validated)

        client = ApiClient(settings.backend_base_url, settings.agent_token)
        try:
            me = client.get_json("/api/agents/me")
        finally:
            client.close()
        log.info("authenticated as %s", me.get("agent_id"))
        audit("authenticated", agent_id=me.get("agent_id"))
        machine.transition_to(AgentState.registered)
    except AgentError as exc:
        log.error("startup failed: %s", exc)
        audit("startup_failed", str(exc))
        return 1

    log.info("ready")
    audit("ready")
    if args.once:
        machine.transition_to(AgentState.stopped)
        return 0
    try:
        asyncio.run(run_forever(settings, machine))
    except KeyboardInterrupt:
        log.info("stopped by user")
        audit("stopped", "keyboard interrupt")
    except AgentError as exc:
        log.error("agent stopped: %s", exc)
        audit("agent_stopped", str(exc))
        return 1
    machine.transition_to(AgentState.stopped)
    return 0


if __name__ == "__main__":
    sys.exit(main())
