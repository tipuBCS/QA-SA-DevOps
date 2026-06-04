from __future__ import annotations

from typing import TypedDict


class UserItem(TypedDict):
    """Raw DynamoDB item shape for a user."""
    PK: str
    SK: str
    GSI1PK: str
    GSI1SK: str
    user_id: str
    email: str
    name: str
    password_hash: str
    salt: str
    is_admin: bool
    access_level: int
    entity_type: str


class User(TypedDict):
    """Cleaned user shape returned by the API."""
    user_id: str
    email: str
    name: str
    is_admin: bool
    access_level: int
    access_level_name: str
