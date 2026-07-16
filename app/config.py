"""
Application configuration.

Settings are loaded from environment variables (and an optional `.env`
file) using pydantic-settings. This keeps secrets and environment-specific
values out of source control -- see `.env.example` for the full list of
supported variables.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General application metadata -------------------------------------------------
    APP_NAME: str = "FastAPI User Management API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "A production-ready CRUD API for user management, built with "
        "FastAPI, SQLAlchemy, and Pydantic."
    )
    ENVIRONMENT: str = "development"  # development | staging | production
    DEBUG: bool = False

    # --- API versioning -----------------------------------------------------------------
    API_V1_PREFIX: str = "/api/v1"

    # --- Database -----------------------------------------------------------------------
    # Defaults to a local SQLite file so the project runs with zero setup.
    # Lives in a `data/` subdirectory (auto-created by database.py) so the
    # exact same relative path also works as a Docker volume mount target.
    # Swap this for a PostgreSQL URL in production, e.g.:
    #   postgresql://user:password@localhost:5432/users_db
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # --- Security -----------------------------------------------------------------------
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- CORS ---------------------------------------------------------------------------
    # Comma separated list of allowed origins, or "*" for all.
    ALLOWED_ORIGINS: str = "*"

    # --- Logging ------------------------------------------------------------------------
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Return ALLOWED_ORIGINS as a list, expanding '*' appropriately."""
        if self.ALLOWED_ORIGINS.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor -- avoids re-parsing the environment on every import."""
    return Settings()


settings = get_settings()
