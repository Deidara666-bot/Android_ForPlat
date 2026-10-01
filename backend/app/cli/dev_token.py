"""Print a JWT for an existing examiner (development helper for `curl`)."""

import argparse
import sys

from app.core.config import get_settings
from app.core.security import create_access_token
from app.db.session import SessionLocal
from app.services.auth_service import AuthService

_ALLOWED_ENVS = ("development", "test")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True)
    args = parser.parse_args(argv)

    app_env = get_settings().app_env
    if app_env not in _ALLOWED_ENVS:
        print(f"refused: APP_ENV={app_env!r} (only {', '.join(_ALLOWED_ENVS)})", file=sys.stderr)
        return 2

    with SessionLocal() as db:
        user = AuthService(db).get_by_email(args.email)
    if user is None:
        print(f"no examiner with e-mail {args.email!r}", file=sys.stderr)
        return 1
    print(create_access_token(str(user.id)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
