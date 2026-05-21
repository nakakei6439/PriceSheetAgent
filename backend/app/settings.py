from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    document_intelligence_endpoint: str = ""
    document_intelligence_key: str = ""

    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_gpt4o_deployment: str = "gpt-4o"
    azure_openai_timeout: float = 60.0
    azure_openai_max_retries: int = 2

    ai_foundry_project_endpoint: str = ""
    ai_foundry_model_deployment: str = "gpt-4o"

    azure_storage_connection_string: str = ""

    cors_origins: str = "http://localhost:3000"
    max_upload_bytes: int = 15 * 1024 * 1024

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
