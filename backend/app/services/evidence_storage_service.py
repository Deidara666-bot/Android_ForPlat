import os
import re
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from app.services.integrity_service import IntegrityService

_OPERATION_ID = re.compile(r"^[a-z][a-z_]{0,63}$")
_CHUNK_BYTES = 1024 * 1024
QUARANTINE_DIR = ".incoming"


class UploadTooLargeError(Exception):
    """The received bytes passed the size limit; the quarantine file is already removed."""


@dataclass(frozen=True)
class QuarantinedUpload:
    """A fully received upload, still outside its final path."""

    path: Path
    size_bytes: int
    sha256: str


class EvidenceStorageService:
    """Receives uploads into a quarantine file, then stores them once, read-only."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._integrity = IntegrityService()

    def resolve(self, stored_path: str) -> Path:
        """Absolute path of a stored file; never leaves EVIDENCE_ROOT."""
        path = (self._root / stored_path).resolve()
        if not path.is_relative_to(self._root):
            raise ValueError("evidence path escapes EVIDENCE_ROOT")
        return path

    def _final_path(
        self, session_id: uuid.UUID, sequence: int, operation_id: str, part: int
    ) -> Path:
        # The file name is built here from typed values only; nothing comes from the client.
        if sequence < 1 or part < 1 or _OPERATION_ID.fullmatch(operation_id) is None:
            raise ValueError("invalid evidence key")
        path = (self._root / str(session_id) / f"{sequence}-{operation_id}-{part}.bin").resolve()
        if not path.is_relative_to(self._root):
            raise ValueError("evidence path escapes EVIDENCE_ROOT")
        return path

    def already_stored(
        self, session_id: uuid.UUID, sequence: int, operation_id: str, part: int
    ) -> bool:
        return self._final_path(session_id, sequence, operation_id, part).exists()

    def receive(self, read: Callable[[int], bytes], max_bytes: int) -> QuarantinedUpload:
        """Stream `read` block by block into `.incoming/<random>`, hashing as it is written.

        Never holds more than one block in memory. Past `max_bytes` the quarantine file is
        removed and `UploadTooLargeError` is raised; any other failure also removes it.
        """
        directory = self._root / QUARANTINE_DIR
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / uuid.uuid4().hex
        hasher = self._integrity.new_hasher()
        size = 0
        try:
            with path.open("xb") as handle:
                while block := read(_CHUNK_BYTES):
                    size += len(block)
                    if size > max_bytes:
                        raise UploadTooLargeError
                    hasher.update(block)
                    handle.write(block)
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        return QuarantinedUpload(path=path, size_bytes=size, sha256=hasher.hexdigest())

    def discard(self, quarantined: QuarantinedUpload) -> None:
        quarantined.path.unlink(missing_ok=True)

    def store_file(
        self,
        session_id: uuid.UUID,
        sequence: int,
        operation_id: str,
        part: int,
        quarantined: QuarantinedUpload,
    ) -> str:
        """Move the quarantine file to its final path without replacing anything, make it
        read-only and return the path relative to EVIDENCE_ROOT (POSIX separators).

        An existing file is never replaced (`FileExistsError`); the quarantine file is removed
        in every case.
        """
        final = self._final_path(session_id, sequence, operation_id, part)
        final.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.link(quarantined.path, final)  # fails if `final` exists: no overwrite, ever
        finally:
            quarantined.path.unlink(missing_ok=True)
        os.chmod(final, 0o444)
        return final.relative_to(self._root).as_posix()

    def store(
        self, session_id: uuid.UUID, sequence: int, operation_id: str, part: int, data: bytes
    ) -> str:
        """Store in-memory bytes through the same quarantine path (small data, fixtures)."""
        self._final_path(session_id, sequence, operation_id, part)  # validate the key first
        chunks = iter([data, b""])
        quarantined = self.receive(lambda _size: next(chunks), len(data))
        return self.store_file(session_id, sequence, operation_id, part, quarantined)
