from typing import TypedDict


class CurrentUser(TypedDict):
    """Shape of the user extracted from a verified JWT token."""
    user_id: str
    email: str
    is_admin: bool
    access_level: int
