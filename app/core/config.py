from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import DirectoryPath


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://app:app@db:5432/calls"
    REDIS_URL: str = "redis://redis:6379/0"
    # Allow string path in containers; DirectoryPath valid after mount
    RECORDINGS_DIR: DirectoryPath | str = "/recordings"

    APP_ENV: str = "dev"
    APP_NAME: str = "CallsService"

    # Optional S3/MinIO settings for presigned URLs
    S3_ENABLED: bool = False
    S3_ENDPOINT_URL: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_BUCKET: str | None = None
    S3_REGION: str | None = "us-east-1"
    S3_SECURE: bool = False

    # Pydantic v2 settings config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",  # allow HOST/PORT etc. in .env
    )


settings = Settings()
