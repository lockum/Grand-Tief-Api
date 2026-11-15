from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "ViceWire API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database Configuration
    DATABASE_PATH: str = "./gta_news.db"

    # Polling & Synchronization (in minutes)
    POLL_INTERVAL_MINUTES: int = 15

    # Rockstar GraphQL Endpoint
    ROCKSTAR_GRAPHQL_URL: str = "https://graph.rockstargames.com/"
    ROCKSTAR_BASE_URL: str = "https://www.rockstargames.com"

    # Security & Authentication (HTTP Basic Auth)
    # Read-Only User Credentials (used by clients, bots, dashboards)
    API_READONLY_USERNAME: str = "reader"
    API_READONLY_PASSWORD: str = "vicewire_read_2026"

    # Admin User Credentials (can trigger manual sync & read)
    API_ADMIN_USERNAME: str = "admin"
    API_ADMIN_PASSWORD: str = "vicewire_admin_2026"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
