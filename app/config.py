#!/usr/bin/env python3
"""Configuration management for Lawmatics MCP Server."""

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Configuration for Lawmatics MCP Server."""

    # Server settings
    host: str = "0.0.0.0"
    mcp_port: int = 8000

    # Logging
    log_level: str = "INFO"
    debug: bool = False

    # Environment
    environment: str = "production"

    # Lawmatics API settings
    lawmatics_base_url: str = "https://api.lawmatics.com/v1/"
    lawmatics_api_key: str | None = None  # For direct API key access (if available)
    lawmatics_timeout: int = 30

    # Lawmatics OAuth settings
    lawmatics_client_id: str | None = None
    lawmatics_client_secret: str | None = None
    lawmatics_redirect_uri: str = "http://localhost:8000/oauth/callback"
    lawmatics_access_token: str | None = None  # Pre-configured access token

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",  # Ignore extra environment variables
    }


# Global config instance
config = Config()


def is_development() -> bool:
    """Check if running in development environment.

    Returns:
        True if in development mode, False otherwise.
    """
    return config.environment.lower() == "development"


def is_debug_enabled() -> bool:
    """Check if debug mode is enabled.

    Returns:
        True if debug is enabled, False otherwise.
    """
    return config.debug or config.log_level.upper() == "DEBUG"
