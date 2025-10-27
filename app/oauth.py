#!/usr/bin/env python3
"""OAuth 2.0 authentication handler for Lawmatics."""

import os
from typing import Any
from urllib.parse import urlencode

import httpx
from loguru import logger

# OAuth endpoints
LAWMATICS_AUTHORIZE_URL = "https://app.lawmatics.com/oauth/authorize"
LAWMATICS_TOKEN_URL = "https://api.lawmatics.com/oauth/token"


class LawmaticsOAuthClient:
    """OAuth 2.0 client for Lawmatics API."""

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
    ):
        """Initialize OAuth client.

        Args:
            client_id: OAuth client ID from Lawmatics
            client_secret: OAuth client secret from Lawmatics
            redirect_uri: Callback URL registered with Lawmatics
        """
        self.client_id = client_id or os.getenv("LAWMATICS_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("LAWMATICS_CLIENT_SECRET")
        self.redirect_uri = redirect_uri or os.getenv("LAWMATICS_REDIRECT_URI")
        self.access_token: str | None = None
        self.refresh_token: str | None = None

    def get_authorization_url(self, state: str | None = None) -> str:
        """Generate OAuth authorization URL.

        Args:
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL to redirect user to
        """
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "read write",  # Adjust scopes as needed
        }

        if state:
            params["state"] = state

        return f"{LAWMATICS_AUTHORIZE_URL}?{urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        """Exchange authorization code for access token.

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Token response with access_token, refresh_token, etc.

        Raises:
            httpx.HTTPStatusError: If token exchange fails
        """
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                LAWMATICS_TOKEN_URL,
                data=data,
                timeout=30.0,
            )
            response.raise_for_status()
            token_data = response.json()

            # Store tokens
            self.access_token = token_data.get("access_token")
            self.refresh_token = token_data.get("refresh_token")

            logger.info("Successfully obtained access token")
            return token_data

    async def refresh_access_token(self) -> dict[str, Any]:
        """Refresh the access token using refresh token.

        Returns:
            New token response

        Raises:
            ValueError: If refresh token is not available
            httpx.HTTPStatusError: If token refresh fails
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                LAWMATICS_TOKEN_URL,
                data=data,
                timeout=30.0,
            )
            response.raise_for_status()
            token_data = response.json()

            # Update tokens
            self.access_token = token_data.get("access_token")
            if "refresh_token" in token_data:
                self.refresh_token = token_data["refresh_token"]

            logger.info("Successfully refreshed access token")
            return token_data

    def get_auth_headers(self) -> dict[str, str]:
        """Get authorization headers for API requests.

        Returns:
            Dictionary with Authorization header

        Raises:
            ValueError: If access token is not available
        """
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")

        return {"Authorization": f"Bearer {self.access_token}"}


# Global OAuth client instance
_oauth_client: LawmaticsOAuthClient | None = None


def get_oauth_client() -> LawmaticsOAuthClient:
    """Get or create the global OAuth client.

    Returns:
        The global OAuth client instance
    """
    global _oauth_client
    if _oauth_client is None:
        _oauth_client = LawmaticsOAuthClient()
    return _oauth_client


def set_access_token(token: str) -> None:
    """Set the access token directly (for API key compatibility).

    Args:
        token: The access token or API key to use
    """
    client = get_oauth_client()
    client.access_token = token
    logger.info("Access token set directly")
