from functools import lru_cache
from typing import Any, Literal

from pydantic import field_validator
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    Application settings.
    """

    app_name: str = "MCP-NLP Server"
    instructions: str = "This server provides NLP tools."

    transport: Literal["streamable-http", "sse"] = "streamable-http"

    allowed_hosts: list[str] = ["*"]
    allowed_methods: list[str] = ["GET", "POST", "OPTIONS"]
    allowed_headers: list[str] = ["*"]
    allow_credentials: bool = True

    # API key authentication
    api_key_enabled: bool = False
    api_key: str | None = None
    api_key_name: str = "X-API-Key"  # Header name

    model_config = SettingsConfigDict(
        env_file=".env",
    )

    @property
    def fastmcp_kwargs(self) -> dict[str, Any]:
        """
        FastAPI related arguments.
        """
        return {
            "name": self.app_name,
            "instructions": self.instructions,
        }

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: str | None, info: FieldValidationInfo) -> str | None:
        """
        Validate API key.
        """
        value = v.strip() if v else None
        if info.data.get("api_key_enabled") and not value:
            raise ValueError("`api_key` must be provided when `api_key_enabled` is True.")
        return value


@lru_cache
def get_app_settings() -> AppSettings:
    """
    Get application settings.
    """
    return AppSettings()
