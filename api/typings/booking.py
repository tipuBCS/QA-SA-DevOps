from __future__ import annotations

from typing import TypedDict


class BookingItem(TypedDict):
    """Raw DynamoDB item shape for a booking."""
    PK: str
    SK: str
    GSI1PK: str
    GSI1SK: str
    GSI2PK: str
    GSI2SK: str
    booking_id: str
    room_id: str
    room_name: str
    building_id: str
    building_name: str
    floor: int
    user_id: str
    date: str
    start_time: str
    end_time: str
    purpose: str
    entity_type: str


class Booking(TypedDict):
    """Cleaned booking shape returned by the API."""
    booking_id: str
    room_id: str
    room_name: str
    building_id: str
    building_name: str
    floor: int
    user_id: str
    date: str
    start_time: str
    end_time: str
    purpose: str
