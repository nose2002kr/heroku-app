from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import Header
from typing import Optional
from loguru import logger

from app.service.user_db import save_user

from config import Config

async def verify_google_token(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """
    Verify Google OAuth token from Authorization header.
    Returns user info if valid, None if invalid or missing.
    Saves user to database on successful authentication.
    """
    if not authorization:
        return None

    try:
        if not authorization.startswith("Bearer "):
            return None

        token = authorization[7:]  # Remove "Bearer " prefix

        if not Config.google_client_id:
            return None

        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            Config.google_client_id
        )

        user_info = {
            "user_id": idinfo.get("sub"),
            "email": idinfo.get("email"),
            "name": idinfo.get("name")
        }

        # Save user to database
        save_user(
            user_id=user_info["user_id"],
            username=user_info["name"] or user_info["email"],
            email=user_info["email"]
        )

        return user_info
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def is_authenticated(user_info: Optional[dict]) -> bool:
    """Check if user is authenticated."""
    return user_info is not None
