from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_ROOT = Path(__file__).resolve().parents[2]
_REPO_ROOT = Path(__file__).resolve().parents[4]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(_REPO_ROOT / ".env"), str(_API_ROOT / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = Field(default="development")
    app_name: str = Field(default="creatoros-api")
    app_version: str = Field(default="0.1.0")
    database_url: str = Field(
        default="postgresql+psycopg://creatoros:creatoros@localhost:5432/creatoros"
    )
    redis_url: str = Field(default="redis://localhost:6379/0")
    secret_key: str = Field(default="replace-this")
    frontend_url: str = Field(default="http://localhost:3000")
    backend_url: str = Field(default="http://localhost:8000")
    request_max_bytes: int = Field(default=1_048_576)
    cors_origins: str = Field(default="")
    access_token_minutes: int = Field(default=60 * 24 * 7)
    ai_api_key: str = Field(default="")
    ai_model: str = Field(default="gpt-4o-mini")
    ai_base_url: str = Field(default="https://api.openai.com/v1")

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("SECRET_KEY must be set")
        return value

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}

    @property
    def allowed_origins(self) -> list[str]:
        extra = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
        origins = [
            self.frontend_url,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            *extra,
        ]
        unique: list[str] = []
        for origin in origins:
            if origin not in unique:
                unique.append(origin)
        return unique


@lru_cache
def get_settings() -> Settings:
    return Settings()
