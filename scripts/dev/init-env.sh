#!/usr/bin/env bash
# Create local .env files from .env.example and replace placeholder secrets with random values.
# Idempotent. Never prints secret values. Usage: bash scripts/dev/init-env.sh

set -u
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

random_hex() { head -c 32 /dev/urandom | od -An -tx1 | tr -d ' \n'; }

for comp in backend agent frontend; do
  ex="$root/$comp/.env.example"
  env="$root/$comp/.env"
  [ -f "$ex" ] || continue
  if [ ! -f "$env" ]; then
    cp "$ex" "$env"
    echo "created $comp/.env"
  else
    echo "exists  $comp/.env"
  fi
done

be="$root/backend/.env"
if [ -f "$be" ] && grep -q '^JWT_SECRET=change-me$' "$be"; then
  sed -i "s/^JWT_SECRET=change-me\$/JWT_SECRET=$(random_hex)/" "$be"
  echo "set     backend/.env JWT_SECRET (random, not shown)"
fi
# AGENT_TOKEN is written by scripts/dev/register-agent.sh (v0.20.2), not here.
