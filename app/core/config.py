from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "ViceWire API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database
    DATABASE_PATH: str = "./gta_news.db"

    # Polling & Synchronization (in minutes)
    POLL_INTERVAL_MINUTES: int = 15

    # Rockstar GraphQL Endpoint
    ROCKSTAR_GRAPHQL_URL: str = "https://graph.rockstargames.com/"
    ROCKSTAR_BASE_URL: str = "https://www.rockstargames.com"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
