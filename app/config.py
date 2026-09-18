from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Enterprise RAG API"
    api_v1_prefix: str = "/api/v1"
    api_key: str = "development-api-key"
    gemini_api_key: str = ""
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_chat_model: str = "gemini-3.6-flash"
    chroma_persist_directory: str = "./chroma_db"
    chroma_collection_name: str = "enterprise_docs"
    chunk_size: int = 1000
    chunk_overlap: int = 150

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
