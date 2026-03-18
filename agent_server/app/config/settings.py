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

    llm_provider: str | None = None # mock / openai / local
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str | None = None
    local_model_name: str | None = None

    knowledge_dir: str = "docs/knowledge"
    rag_top_k: int = 3
    rag_chunk_size: int = 300
    rag_chunk_overlap: int = 50
    policy_handbook_enabled: bool = True
    policy_handbook_sql_top_k: int = 3
    policy_handbook_vector_top_k: int = 3
    policy_handbook_jsonl_path: str = "docs/knowledge/policy_handbook_nodes.jsonl"
    policy_handbook_auto_seed_on_startup: bool = True

    embedding_provider: str = "local"   # local / openai
    embedding_api_key: str | None = None
    embedding_base_url: str | None = None
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int | None = None

@lru_cache
def get_settings() -> Settings:
    return Settings()