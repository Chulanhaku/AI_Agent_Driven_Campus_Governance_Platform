from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "ai_school_agent_server"
    app_env: str = "dev"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    debug: bool = True

    database_url: str = "postgresql+psycopg2://postgres:123456@127.0.0.1:5432/ai_school_db"

    jwt_secret_key: str = "replace_me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 120


@lru_cache
def get_settings() -> Settings:
    return Settings()