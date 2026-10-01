import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User

# Verified against when the e-mail is unknown, so both failure paths cost about the same.
_DUMMY_HASH = hash_password("not-a-real-password")


class AuthService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def authenticate(self, email: str, password: str) -> User | None:
        user = self._db.scalar(select(User).where(User.email == email))
        if user is None:
            verify_password(password, _DUMMY_HASH)
            return None
        return user if verify_password(password, user.password_hash) else None

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._db.scalar(select(User).where(User.email == email))
