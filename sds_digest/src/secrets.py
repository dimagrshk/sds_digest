from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Secrets(BaseSettings):
    openai_api_key: str | None
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
