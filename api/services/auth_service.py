import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

from aws_lambda_powertools import Logger

logger = Logger()

# Secret key for signing tokens — must be set in environment
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = int(os.environ.get("JWT_EXPIRY_HOURS", "1"))


class AuthService:
    """Handles JWT token creation and verification."""

    @staticmethod
    def create_token(
        user_id: str,
        email: str,
        is_admin: bool,
        access_level: int,
    ) -> str:
        """Create a signed JWT token for an authenticated user."""
        now = datetime.now(tz=timezone.utc)
        payload = {
            "sub": user_id,
            "email": email,
            "is_admin": is_admin,
            "access_level": access_level,
            "iat": now,
            "exp": now + timedelta(hours=JWT_EXPIRY_HOURS),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decode and verify a JWT token.

        Returns the payload dict on success.
        Raises ValueError on invalid or expired tokens.
        """
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")

    @staticmethod
    def get_user_from_token(token: str) -> dict:
        """
        Extract user info from a valid token.

        Returns a dict with user_id, email, is_admin, access_level.
        Raises ValueError if token is invalid.
        """
        payload = AuthService.decode_token(token)
        return {
            "user_id": payload["sub"],
            "email": payload["email"],
            "is_admin": payload.get("is_admin", False),
            "access_level": payload.get("access_level", 1),
        }

    @staticmethod
    def extract_token_from_header(authorization_header: Optional[str]) -> str:
        """
        Extract the token from a Bearer authorization header.

        Expected format: "Bearer <token>"
        Raises ValueError if header is missing or malformed.
        """
        if not authorization_header:
            raise ValueError("Missing Authorization header")

        parts = authorization_header.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise ValueError("Invalid Authorization header format. Expected: Bearer <token>")

        return parts[1]
