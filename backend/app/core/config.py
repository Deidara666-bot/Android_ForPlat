from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
_PLACEHOLDER_SECRET = "change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="ignore")

    app_env: str = "development"
    database_url: str
    evidence_root: str = "./var/evidence"
    jwt_secret: str
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def _reject_placeholder_secret(self) -> "Settings":
        if self.jwt_secret == _PLACEHOLDER_SECRET and self.app_env != "test":
            raise ValueError("JWT_SECRET must not be the placeholder value outside APP_ENV=test")
        if "*" in self.cors_origins:
            raise ValueError("CORS_ORIGINS must list explicit origins, not '*'")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
