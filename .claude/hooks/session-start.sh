#!/usr/bin/env bash
# SessionStart hook for Android_ForPlat.
# 1) Idempotently applies the per-clone git config (so the user never runs it by hand).
# 2) Fetches origin and prints a short repo status; stdout becomes context for Claude.
# Runs under Git Bash on Windows and bash on Linux/macOS (local and claude.ai cloud sessions).
# Never commits, merges, or pushes — it only configures and reports.

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0
export GIT_TERMINAL_PROMPT=0

# ---- 1. per-clone config -------------------------------------------------
changed=""
ensure() {
  if [ "$(git config --local --get "$1" 2>/dev/null)" != "$2" ]; then
    git config --local "$1" "$2" && changed="$changed $1=$2"
  fi
}
ensure core.hooksPath .githooks
ensure core.autocrlf false
chmod +x .githooks/* .claude/hooks/*.sh 2>/dev/null

# ---- 2. fetch origin (bounded) --------------------------------------------
fetch="ok"
if command -v timeout >/dev/null 2>&1; then
  timeout 25 git fetch --quiet --prune origin >/dev/null 2>&1 || fetch="failed (offline/auth?)"
else
  git fetch --quiet --prune origin >/dev/null 2>&1 || fetch="failed (offline/auth?)"
fi

# ---- 3. status ------------------------------------------------------------
if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then env_kind="cloud (claude.ai) - no ADB/AVD/Docker"; else env_kind="local"; fi

branch=$(git branch --show-current 2>/dev/null)
[ -z "$branch" ] && branch="(detached HEAD)"
dirty=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

ahead_behind() { # $1=local ref $2=remote ref -> "ahead A, behind B"
  if git rev-parse --verify --quiet "$2" >/dev/null; then
    set -- $(git rev-list --left-right --count "$1...$2" 2>/dev/null)
    echo "ahead ${1:-?}, behind ${2:-?}"
  else
    echo "no remote ref"
  fi
}
cur_sync=$(ahead_behind HEAD "origin/$branch")
main_sync="n/a"
git rev-parse --verify --quiet main >/dev/null && main_sync=$(ahead_behind main origin/main)

if git remote get-url gitlab >/dev/null 2>&1; then
  gitlab_mode="push - local remote 'gitlab' exists; push origin first, then gitlab"
else
  gitlab_mode="mirror - GitLab follows GitHub automatically; push to origin only"
fi
gitlab_url=$(git config --local --get forplat.gitlabUrl 2>/dev/null)

pending=""
base="main"
git rev-parse --verify --quiet main >/dev/null || base="origin/main"
for ref in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/claude/ 2>/dev/null); do
  if ! git merge-base --is-ancestor "$ref" "$base" 2>/dev/null; then
    n=$(git rev-list --count "$base..$ref" 2>/dev/null)
    pending="$pending
    - $ref ($n commit belum di $base)"
  fi
done

# ---- 4. report ------------------------------------------------------------
echo "[forplat session-start]"
echo "  env            : $env_kind"
echo "  git config     : ${changed:-ok (hooksPath/autocrlf already set)}"
echo "  fetch origin   : $fetch"
echo "  branch         : $branch | uncommitted files: $dirty | vs origin: $cur_sync"
echo "  main           : vs origin/main: $main_sync"
echo "  gitlab         : $gitlab_mode${gitlab_url:+ | url: $gitlab_url}"
if [ -n "$pending" ]; then
  echo "  cloud branches waiting to be integrated into main:$pending"
fi

hints=""
case "$main_sync" in ahead\ [1-9]*) hints="$hints
  - main has local commits not on GitHub -> offer /sync main" ;; esac
case "$main_sync" in *behind\ [1-9]*) hints="$hints
  - origin/main has new commits -> pull before new work" ;; esac
[ -n "$pending" ] && [ "$env_kind" = "local" ] && hints="$hints
  - offer /integrate to merge the cloud branches above into main"
[ "$dirty" != "0" ] && hints="$hints
  - working tree has uncommitted changes -> ask before switching branches"
if [ -n "$hints" ]; then
  echo "  suggested actions (ask the user first):$hints"
fi
exit 0
