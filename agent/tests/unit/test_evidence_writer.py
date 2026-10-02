from pathlib import Path

import pytest

from src.acquisition.evidence_writer import write_evidence


def test_writer_writes_bytes_exactly_and_returns_size(tmp_path: Path) -> None:
    data = b"line1\r\nline2\n  trailing space \x00\xff"
    path = tmp_path / "1-collect_device_metadata.bin"
    assert write_evidence(path, data) == len(data)
    assert path.read_bytes() == data


def test_writer_creates_parent_folders(tmp_path: Path) -> None:
    path = tmp_path / "session" / "nested" / "1-op.bin"
    write_evidence(path, b"x")
    assert path.read_bytes() == b"x"


def test_writer_refuses_existing_path_and_keeps_old_content(tmp_path: Path) -> None:
    path = tmp_path / "1-op.bin"
    write_evidence(path, b"satu")
    with pytest.raises(FileExistsError):
        write_evidence(path, b"dua")
    assert path.read_bytes() == b"satu"
