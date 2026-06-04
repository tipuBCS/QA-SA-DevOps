from __future__ import annotations

from typing import List, TypedDict


class RoomItem(TypedDict):
    """Raw DynamoDB item shape for a room."""
    PK: str
    SK: str
    GSI1PK: str
    GSI1SK: str
    room_id: str
    building_id: str
    building_name: str
    floor: int
    name: str
    capacity: int
    min_access_level: int
    min_access_level_name: str
    room_type_id: str
    room_type_name: str
    amenities: List[str]
    entity_type: str


class Room(TypedDict):
    """Cleaned room shape returned by the API."""
    room_id: str
    building_id: str
    building_name: str
    floor: int
    name: str
    capacity: int
    min_access_level: int
    min_access_level_name: str
    room_type_id: str
    room_type_name: str
    amenities: List[str]
