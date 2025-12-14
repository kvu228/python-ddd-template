"""Application settings using Pydantic BaseSettings."""

from enum import Enum
from typing import Optional

from pydantic import BaseSettings, Field, PostgresDsn, validator


class Environment(str, Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Shop Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = Field(default=False, env="DEBUG")
    API_V1_PREFIX: str = "/api/v1"

    # PostgreSQL (Write Model)
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="postgres", env="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="shop_db", env="POSTGRES_DB")
    POSTGRES_URL: Optional[PostgresDsn] = None

    @validator("POSTGRES_URL", pre=True)
    def assemble_postgres_connection(cls, v: Optional[str], values: dict) -> str:
        """Assemble PostgreSQL connection URL."""
        if isinstance(v, str):
            return v
        return (
            f"postgresql://{values.get('POSTGRES_USER')}:"
            f"{values.get('POSTGRES_PASSWORD')}@"
            f"{values.get('POSTGRES_HOST')}:"
            f"{values.get('POSTGRES_PORT')}/"
            f"{values.get('POSTGRES_DB')}"
        )

    # Redis (Cache & Celery Broker)
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0", env="REDIS_URL"
    )

    # MongoDB (Read Model)
    MONGODB_HOST: str = Field(default="localhost", env="MONGODB_HOST")
    MONGODB_PORT: int = Field(default=27017, env="MONGODB_PORT")
    MONGODB_DB: str = Field(default="shop_read_db", env="MONGODB_DB")
    MONGODB_USER: Optional[str] = Field(default=None, env="MONGODB_USER")
    MONGODB_PASSWORD: Optional[str] = Field(default=None, env="MONGODB_PASSWORD")
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017/shop_read_db", env="MONGODB_URL"
    )

    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1", env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2", env="CELERY_RESULT_BACKEND"
    )

    # Email Service
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USER: Optional[str] = Field(default=None, env="SMTP_USER")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    EMAIL_FROM: Optional[str] = Field(default=None, env="EMAIL_FROM")

    # Cache TTL (seconds)
    USER_CACHE_TTL: int = Field(default=3600, env="USER_CACHE_TTL")  # 1 hour
    ORDER_CACHE_TTL: int = Field(default=1800, env="ORDER_CACHE_TTL")  # 30 minutes

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "%(message)s"
    )

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()


