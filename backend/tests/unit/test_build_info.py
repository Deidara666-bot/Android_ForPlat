"""`code_commit`: the commit that produced an analysis (REF §ENGINE "Run")."""

import subprocess
from pathlib import Path

import pytest

from app.core.build_info import is_verified_commit, read_code_commit


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.test", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    (tmp_path / "tracked.txt").write_text("one\n", encoding="utf-8")
    _git(tmp_path, "add", "tracked.txt")
    _git(tmp_path, "commit", "-q", "-m", "first")
    return tmp_path


def test_a_clean_repository_gives_the_head_sha(repo: Path) -> None:
    sha = _git(repo, "rev-parse", "HEAD")
    assert read_code_commit(repo) == sha and len(sha) == 40


def test_a_tracked_change_makes_the_commit_dirty(repo: Path) -> None:
    sha = _git(repo, "rev-parse", "HEAD")
    (repo / "tracked.txt").write_text("two\n", encoding="utf-8")
    assert read_code_commit(repo) == f"{sha}-dirty"


def test_an_untracked_file_does_not_make_the_commit_dirty(repo: Path) -> None:
    (repo / "scratch.txt").write_text("x\n", encoding="utf-8")
    assert read_code_commit(repo) == _git(repo, "rev-parse", "HEAD")


def test_a_folder_that_is_not_a_repository_is_unknown(tmp_path: Path) -> None:
    assert read_code_commit(tmp_path) == "unknown"


def test_a_missing_folder_is_unknown(tmp_path: Path) -> None:
    assert read_code_commit(tmp_path / "does-not-exist") == "unknown"


def test_a_repository_without_a_commit_is_unknown(tmp_path: Path) -> None:
    _git(tmp_path, "init", "-q")
    assert read_code_commit(tmp_path) == "unknown"


@pytest.mark.parametrize(
    ("commit", "verified"),
    [("a" * 40, True), ("a" * 40 + "-dirty", False), ("unknown", False)],
)
def test_only_a_clean_known_commit_is_verified(commit: str, verified: bool) -> None:
    assert is_verified_commit(commit) is verified


def test_the_real_repository_gives_a_commit_or_unknown() -> None:
    commit = read_code_commit()
    assert commit == "unknown" or len(commit.removesuffix("-dirty")) == 40
