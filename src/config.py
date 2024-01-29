from typing import Any

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings

from src.auth.schemas import AuthUser
from src.constants import Environment


class Config(BaseSettings):
    DATABASE_URL: PostgresDsn
    SYNC_DATABASE_URL: str
    REDIS_URL: RedisDsn
    SITE_DOMAIN: str
    CORS_ORIGINS: list[str]
    CORS_ORIGINS_REGEX: str | None = None
    CORS_HEADERS: list[str]
    ENVIRONMENT: Environment = Environment.TESTING
    APP_VERSION: str = "1"


settings = Config()

app_configs: dict[str, Any] = {"title": "App API", "securityScheme": {
        "OAuth2PasswordBearer": AuthUser
    }}
if settings.ENVIRONMENT.is_deployed:
    app_configs["root_path"] = f"/v{settings.APP_VERSION}"

if not settings.ENVIRONMENT.is_debug:
    app_configs["openapi_url"] = None  # hide docs
