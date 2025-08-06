"""Configuration settings for PersonaKit."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql+asyncpg://personakit:personakit_dev@localhost:5436/personakit"
    database_url_sync: str = "postgresql://personakit:personakit_dev@localhost:5436/personakit"
    db_pool_size: int = 20
    db_max_overflow: int = 0

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8042
    api_reload: bool = True

    # Application
    app_name: str = "PersonaKit"
    app_version: str = "0.1.0"
    environment: str = "development"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Performance
    request_timeout: int = 10

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"


# Global settings instance
settings = Settings()
