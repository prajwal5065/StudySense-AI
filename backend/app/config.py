"""Settings loader. Reads .env; never raises if GEMINI_API_KEY is blank."""
from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = ""
    gemini_text_model: str = "gemini-2.0-flash"
    gemini_vision_model: str = "gemini-2.0-flash"
    gemini_embed_model: str = "text-embedding-004"

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:8080,http://localhost:5173,http://localhost:3000"

    data_dir: str = "./data"
    max_workers: int = 4
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def data_path(self) -> Path:
        p = Path(self.data_dir).resolve()
        p.mkdir(parents=True, exist_ok=True)
        (p / "uploads").mkdir(exist_ok=True)
        return p

    @property
    def db_path(self) -> Path:
        return self.data_path / "studysmart.db"

    @property
    def has_key(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key.strip())


settings = Settings()