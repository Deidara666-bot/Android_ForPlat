import os
import re
import uuid
from pathlib import Path

_OPERATION_ID = re.compile(r"^[a-z][a-z_]{0,63}$")


class EvidenceStorageService:
    """Writes raw evidence under EVIDENCE_ROOT, once, and makes it read-only."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()

    def store(
        self, session_id: uuid.UUID, sequence: int, operation_id: str, part: int, data: bytes
    ) -> str:
        """Store `data` and return its path relative to EVIDENCE_ROOT (POSIX separators).

        The file name is built here from typed values only; nothing comes from the client's
        file name. An existing file is never replaced (`FileExistsError`).
        """
        if sequence < 1 or part < 1 or _OPERATION_ID.fullmatch(operation_id) is None:
            raise ValueError("invalid evidence key")
        path = (self._root / str(session_id) / f"{sequence}-{operation_id}-{part}.bin").resolve()
        if not path.is_relative_to(self._root):
            raise ValueError("evidence path escapes EVIDENCE_ROOT")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(data)
        os.chmod(path, 0o444)
        return path.relative_to(self._root).as_posix()
