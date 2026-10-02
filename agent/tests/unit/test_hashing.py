from pathlib import Path

from src.integrity.hashing import sha256_file

_EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_hashing_empty_file_matches_known_digest(tmp_path: Path) -> None:
    path = tmp_path / "empty.bin"
    path.write_bytes(b"")
    assert sha256_file(path) == _EMPTY_SHA256


def test_hashing_one_byte_difference_changes_digest(tmp_path: Path) -> None:
    a, b = tmp_path / "a.bin", tmp_path / "b.bin"
    a.write_bytes(b"package:com.example uid:10001")
    b.write_bytes(b"package:com.example uid:10002")
    assert sha256_file(a) != sha256_file(b)


def test_hashing_spans_multiple_blocks_and_is_lowercase_hex(tmp_path: Path) -> None:
    import hashlib

    data = b"\x00\xff" * (1024 * 1024 + 7)  # larger than one 1 MiB block
    path = tmp_path / "big.bin"
    path.write_bytes(data)
    digest = sha256_file(path)
    assert digest == hashlib.sha256(data).hexdigest()
    assert digest == digest.lower()
