import hashlib
from pathlib import Path

_BLOCK_SIZE = 1024 * 1024  # 1 MiB


def sha256_file(path: Path) -> str:
    """Lowercase hex SHA-256 of the file's bytes, read in 1 MiB blocks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(_BLOCK_SIZE):
            digest.update(block)
    return digest.hexdigest()
