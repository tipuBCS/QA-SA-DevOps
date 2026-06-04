from __future__ import annotations

from typing import TypedDict


class RoomTypeItem(TypedDict):
    """Raw DynamoDB item shape for a room type."""
    PK: str
    SK: str
    GSI1PK: str
    GSI1SK: str
    room_type_id: str
    name: str
    description: str
    entity_type: str


class RoomType(TypedDict):
    """Cleaned room type shape returned by the API."""
    room_type_id: str
    name: str
    description: str
