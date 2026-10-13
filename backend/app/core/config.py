from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App Basics
    app_name: str = "Trade Copilot"
    environment: str = "development"
    api_version: str = "/api/v1"

    # PostgreSQL Configuration
    # Default values match the docker-compose.yml setup
    database_url: str = Field(
        default="postgresql://trade:trade@localhost:5432/tradecopilot",
        validation_alias="DATABASE_URL"
    )

    # Redis Configuration (for Celery)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL"
    )

    # Security / JWT
    jwt_secret: str = Field(
        default="development_secret_key_change_me_in_production",
        validation_alias="JWT_SECRET"
    )
    jwt_algorithm: str = "HS256"
    token_expire_minutes: int = 60 * 24 # 24 hours

    # Model config to enable .env file loading
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
