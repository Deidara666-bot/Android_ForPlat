import os

# Must run before `app` is imported: settings are read at import time by app.main.
os.environ["APP_ENV"] = "test"
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://u:p@localhost:5432/x")
os.environ.setdefault("JWT_SECRET", "change-me")
