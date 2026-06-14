from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    email_lambda_function_name: str | None = Field(
        default=None, alias="EMAIL_LAMBDA_FUNCTION_NAME"
    )
    aws_region: str = Field(default="us-east-1", alias="AWS_REGION")
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        alias="CORS_ORIGINS",
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        cleaned = self.cors_origins.strip()

        if cleaned == "*":
            return ["*"]

        if cleaned.startswith("[") and cleaned.endswith("]"):
            cleaned = cleaned[1:-1]
            cleaned = cleaned.replace('"', "").replace("'", "")

        return [origin.strip() for origin in cleaned.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
