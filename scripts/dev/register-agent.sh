#!/usr/bin/env bash
# Register the dev agent and write its token into agent/.env (token is never printed).
# Reads only the AGENT_ID line of agent/.env. Usage: bash scripts/dev/register-agent.sh

set -eu
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
env_file="$root/agent/.env"
[ -f "$env_file" ] || { echo "agent/.env missing: run scripts/dev/init-env.sh" >&2; exit 1; }

agent_id="$(grep '^AGENT_ID=' "$env_file" | head -n 1 | cut -d= -f2- | tr -d '\r')"
[ -n "$agent_id" ] || { echo "AGENT_ID not set in agent/.env" >&2; exit 1; }

py=""
for p in "$root/backend/.venv/Scripts/python.exe" "$root/backend/.venv/bin/python"; do
  [ -x "$p" ] && { py="$p"; break; }
done
[ -n "$py" ] || { echo "backend/.venv not found" >&2; exit 1; }

cd "$root/backend"
"$py" -m app.cli.register_agent --agent-id "$agent_id" --version 0.20.0 --write-env ../agent/.env
