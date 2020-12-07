# https://fastapi.tiangolo.com/advanced/settings/
from pathlib import Path

from functools import lru_cache
import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, HttpUrl, PostgresDsn, validator, AnyUrl, BaseModel


class MongoDsn(AnyUrl):
    allowed_schemes = {'mongodb'}
    user_required = True


class Settings(BaseSettings):
    API_STR: str = "/api"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    TOKEN: str = secrets.token_urlsafe(32)
    PREDICTED_STORE: Path = Path("/tmp/")
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str
    SERVER_HOST: AnyHttpUrl

    PROJECT_NAME: str
    SENTRY_DSN: Optional[HttpUrl] = None

    @validator("SENTRY_DSN", pre=True)
    def sentry_dsn_can_be_blank(cls, v: str) -> Optional[str]:
        if len(v) == 0:
            return None
        return v

    MONGO_SERVER: str
    MONGO_DB: str
    MONGO_USER: str
    MONGO_PASSWORD: str

    MONGO_DATABASE_URI: Optional[MongoDsn] = None

    @validator("MONGO_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return MongoDsn.build(
            scheme="mongodb",
            user=values.get("MONGO_USER"),
            password=values.get("MONGO_PASSWORD"),
            host=values.get("MONGO_SERVER"),
            # path=f"/{values.get('MONGO_DB') or ''}",
        )

    # POSTGRES_SERVER: str
    # POSTGRES_USER: str
    # POSTGRES_PASSWORD: str
    # POSTGRES_DB: str
    # SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    #
    # @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    # def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
    #     if isinstance(v, str):
    #         return v
    #     return PostgresDsn.build(
    #         scheme="postgresql",
    #         user=values.get("POSTGRES_USER"),
    #         password=values.get("POSTGRES_PASSWORD"),
    #         host=values.get("POSTGRES_SERVER"),
    #         path=f"/{values.get('POSTGRES_DB') or ''}",
    #     )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()


@lru_cache()
def get_settings():
    return Settings()
