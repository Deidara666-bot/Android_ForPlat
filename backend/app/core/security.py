from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

_ALGORITHM = "HS256"
_TOKEN_TTL = timedelta(minutes=60)
_hasher = PasswordHash.recommended()  # argon2


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return _hasher.verify(password, password_hash)


def create_access_token(sub: str) -> str:
    now = datetime.now(UTC)
    payload = {"sub": sub, "iat": now, "exp": now + _TOKEN_TTL}
    return jwt.encode(payload, get_settings().jwt_secret, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, object]:
    """Raise `jwt.InvalidTokenError` (incl. expiry) when the token is not valid."""
    return jwt.decode(token, get_settings().jwt_secret, algorithms=[_ALGORITHM])
