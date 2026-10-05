import hashlib


class IntegrityService:
    """SHA-256 helpers. The server always computes its own digest from the bytes it received."""

    def new_hasher(self) -> "hashlib._Hash":
        return hashlib.sha256()

    def sha256_bytes(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def matches(self, a: str, b: str) -> bool:
        return a.lower() == b.lower()
