"""Create an examiner account. The password is read with getpass, never from argv or env."""

import argparse
import getpass
import sys

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    args = parser.parse_args(argv)

    with SessionLocal() as db:
        if AuthService(db).get_by_email(args.email) is not None:
            print(f"examiner {args.email!r} already exists; nothing changed")
            return 0
        password = getpass.getpass("Password: ")
        if not password or password != getpass.getpass("Repeat password: "):
            print("password empty or not matching; nothing created", file=sys.stderr)
            return 1
        db.add(User(email=args.email, password_hash=hash_password(password)))
        db.commit()
    print(f"examiner {args.email!r} created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
