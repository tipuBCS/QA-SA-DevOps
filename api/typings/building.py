from __future__ import annotations

from typing import TypedDict


class BuildingItem(TypedDict):
    """Raw DynamoDB item shape for a building."""
    PK: str
    SK: str
    GSI1PK: str
    GSI1SK: str
    building_id: str
    name: str
    address: str
    num_floors: int
    entity_type: str


class Building(TypedDict):
    """Cleaned building shape returned by the API."""
    building_id: str
    name: str
    address: str
    num_floors: int
