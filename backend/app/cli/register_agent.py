"""Register an agent and write its token into the agent's .env. The token is never printed."""

import argparse
import sys
from pathlib import Path

from app.db.session import SessionLocal
from app.services.agent_service import AgentService

_KEY = "AGENT_TOKEN"


def write_token(env_file: Path, token: str) -> None:
    lines = env_file.read_text(encoding="utf-8").splitlines() if env_file.exists() else []
    replaced = [f"{_KEY}={token}" if line.startswith(f"{_KEY}=") else line for line in lines]
    if not any(line.startswith(f"{_KEY}=") for line in lines):
        replaced.append(f"{_KEY}={token}")
    env_file.write_text("\n".join(replaced) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--write-env", required=True, type=Path)
    args = parser.parse_args(argv)

    with SessionLocal() as db:
        token = AgentService(db).register(args.agent_id, args.version)
    write_token(args.write_env, token)
    print(f"agent {args.agent_id!r} registered; token written to {args.write_env}", file=sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
