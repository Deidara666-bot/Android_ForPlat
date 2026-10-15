"""Which code produced an analysis (`correlation_runs.code_commit`, REF §ENGINE "Run").

Read once when the backend starts. The commit is `git rev-parse HEAD`; a working tree with
tracked changes makes it `<sha>-dirty`, and anything that fails (no git, not a repository, a
timeout) makes it `unknown`. A `holdout` run refuses both, so a result can always be traced to
code that is in the repository. The commit is read at startup, so restart the backend after a
commit before a holdout run.
"""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

UNKNOWN_COMMIT = "unknown"
DIRTY_SUFFIX = "-dirty"
_REPO_ROOT = Path(__file__).resolve().parents[3]  # backend/app/core/build_info.py -> repository
_TIMEOUT_SECONDS = 10


def _git(repo_root: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(  # noqa: S603 - fixed argument list, no shell
            ["git", *args],  # noqa: S607
            cwd=repo_root,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        logger.warning("git %s failed: %s", args[0], error)
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def read_code_commit(repo_root: Path | None = None) -> str:
    """`<sha>`, `<sha>-dirty` or `unknown` for the repository at `repo_root`."""
    root = repo_root or _REPO_ROOT
    sha = _git(root, "rev-parse", "HEAD")
    if not sha:
        return UNKNOWN_COMMIT
    changes = _git(root, "status", "--porcelain", "--untracked-files=no")
    if changes is None:
        return UNKNOWN_COMMIT  # cannot tell whether the tree is clean: not a verified commit
    return f"{sha}{DIRTY_SUFFIX}" if changes else sha


def is_verified_commit(code_commit: str) -> bool:
    """Whether the commit names code that is in the repository (not dirty, not unknown)."""
    return code_commit != UNKNOWN_COMMIT and not code_commit.endswith(DIRTY_SUFFIX)
