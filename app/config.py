from functools import lru_cache
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug_mode: bool = False

    model_name: str
    transformers_cache: str = "/app/model_cache"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    @model_validator(mode="after")
    def validate_model_name(self):
        if not self.model_name:
            raise ValueError("MODEL_NAME must be provided")
        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
