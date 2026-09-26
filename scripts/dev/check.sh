#!/usr/bin/env bash
# Quality gate for Android_ForPlat. Used by every plan card (docs/dev) before commit.
# Usage: bash scripts/dev/check.sh [all|backend|agent|frontend]
# Works in Git Bash (Windows, .venv/Scripts) and Linux/macOS (.venv/bin).
# Prints only failures plus one summary line; exit code 0 = all enabled checks passed.

set -u
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
target="${1:-all}"
fail=0

venv_python() { # $1 = component dir
  local p
  for p in "$1/.venv/Scripts/python.exe" "$1/.venv/bin/python"; do
    [ -x "$p" ] && { echo "$p"; return 0; }
  done
  return 1
}

step() { # $1 = label, rest = command (run in current dir)
  local label="$1"; shift
  local out
  if ! out=$("$@" 2>&1); then
    echo "FAIL [$label]"
    printf '%s\n' "$out" | tail -n 40
    fail=1
  fi
}

check_python() { # $1 = component, $2 = package dir for mypy
  local dir="$root/$1" py
  if [ ! -f "$dir/pyproject.toml" ]; then echo "SKIP [$1] no pyproject.toml yet"; return; fi
  if ! py=$(venv_python "$dir"); then echo "FAIL [$1] no .venv"; fail=1; return; fi
  pushd "$dir" >/dev/null || return
  step "$1 ruff" "$py" -m ruff check -q .
  step "$1 format" "$py" -m ruff format --check -q .
  step "$1 mypy" "$py" -m mypy "$2"
  step "$1 pytest" "$py" -m pytest -q -p no:cacheprovider
  popd >/dev/null || return
}

check_frontend() {
  local dir="$root/frontend"
  if [ ! -f "$dir/package.json" ]; then echo "SKIP [frontend] no package.json yet"; return; fi
  if [ ! -d "$dir/node_modules" ]; then echo "FAIL [frontend] node_modules missing (npm ci)"; fail=1; return; fi
  pushd "$dir" >/dev/null || return
  step "frontend lint" npm run --silent lint
  step "frontend build" npm run --silent build
  popd >/dev/null || return
}

case "$target" in
  backend)  check_python backend app ;;
  agent)    check_python agent src ;;
  frontend) check_frontend ;;
  all)      check_python backend app; check_python agent src; check_frontend ;;
  *) echo "usage: check.sh [all|backend|agent|frontend]"; exit 2 ;;
esac

if [ "$fail" -eq 0 ]; then echo "CHECK OK ($target)"; else echo "CHECK FAILED ($target)"; fi
exit "$fail"
