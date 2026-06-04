import os
from re import S
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from typing import cast, List, Optional

from boto3.dynamodb.types import TypeSerializer

from typings.room import Room, RoomItem
from models.room import CreateRoomRequest
from models.user import AccessLevel
from services.building_service import BuildingService
from services.room_type_service import RoomTypeService


class RoomService:
    def __init__(self, table_resource=None):
        """
        Accept an optional table resource for dependency injection (testing).
        If not provided, uses the real DynamoDB table from environment.
        """
        if table_resource:
            self.table = table_resource
        else:
            dynamodb = boto3.resource("dynamodb")
            table_name = os.environ.get("DB_TABLE_NAME", "room-booker")
            self.table = dynamodb.Table(table_name)
        self.building_service = BuildingService(table_resource=self.table)
        self.room_type_service = RoomTypeService(table_resource=self.table)

    def create_room(self, request: CreateRoomRequest) -> Room:
        """Create a room in a building on a specific floor."""
        # Validate building exists
        building = self.building_service.get_building(request.building_id)

        # Validate floor number
        if request.floor < 1 or request.floor > building["num_floors"]:
            raise ValueError(f"Floor must be between 1 and {building['num_floors']}")

        # Validate access level
        if not AccessLevel.is_valid(request.min_access_level):
            raise ValueError("Invalid access level")

        # Validate and resolve room type if provided
        room_type_name = ""
        if request.room_type_id:
            room_type = self.room_type_service.get_room_type(request.room_type_id)
            room_type_name = room_type["name"]

        room_id = str(uuid.uuid4())

        item: RoomItem = {
            "PK": f"BUILDING#{request.building_id}",
            "SK": f"ROOM#{room_id}",
            "GSI1PK": "ROOMS",
            "GSI1SK": f"BUILDING#{request.building_id}#FLOOR#{request.floor}",
            "room_id": room_id,
            "building_id": request.building_id,
            "building_name": building["name"],
            "floor": request.floor,
            "name": request.name,
            "capacity": request.capacity,
            "min_access_level": request.min_access_level,
            "min_access_level_name": AccessLevel.name_for(request.min_access_level),
            "room_type_id": request.room_type_id,
            "room_type_name": room_type_name,
            "amenities": request.amenities,
            "entity_type": "ROOM",
        }

        # Casted as dict to stop type error
        self.table.put_item(Item=cast(dict, item))
        
        return {
            "room_id": room_id,
            "building_id": request.building_id,
            "building_name": building["name"],
            "floor": request.floor,
            "name": request.name,
            "capacity": request.capacity,
            "min_access_level": request.min_access_level,
            "min_access_level_name": AccessLevel.name_for(request.min_access_level),
            "room_type_id": request.room_type_id,
            "room_type_name": room_type_name,
            "amenities": request.amenities,
        }

    def get_room(self, building_id: str, room_id: str) -> Room:
        """Get a room by building ID and room ID."""
        result = self.table.get_item(
            Key={"PK": f"BUILDING#{building_id}", "SK": f"ROOM#{room_id}"}
        )
        item = result.get("Item")
        if not item:
            raise ValueError("Room not found")
        item = cast(RoomItem, item)

        return {
            "room_id": item["room_id"],
            "building_id": item["building_id"],
            "building_name": item["building_name"],
            "floor": int(item["floor"]),
            "name": item["name"],
            "capacity": int(item["capacity"]),
            "min_access_level": int(item["min_access_level"]),
            "min_access_level_name": AccessLevel.name_for(
                int(item["min_access_level"])
            ),
            "room_type_id": item.get("room_type_id", ""),
            "room_type_name": item.get("room_type_name", ""),
            "amenities": item.get("amenities", []),
        }

    def list_rooms(self, building_id: Optional[str] = None) -> List[Room]:
        """List rooms, optionally filtered by building."""
        if building_id:
            result = self.table.query(
                KeyConditionExpression=Key("PK").eq(f"BUILDING#{building_id}")
                & Key("SK").begins_with("ROOM#"),
            )
        else:
            result = self.table.query(
                IndexName="GSI1",
                KeyConditionExpression=Key("GSI1PK").eq("ROOMS"),
            )

        roomList: List[Room] = []

        for item in result.get("Items", []):
            item = cast(RoomItem, item)
            room: Room = {
                "room_id": item["room_id"],
                "building_id": item["building_id"],
                "building_name": item["building_name"],
                "floor": int(item["floor"]),
                "name": item["name"],
                "capacity": int(item["capacity"]),
                "min_access_level": int(item["min_access_level"]),
                "min_access_level_name": AccessLevel.name_for(
                    int(item["min_access_level"])
                ),
                "room_type_id": item.get("room_type_id", ""),
                "room_type_name": item.get("room_type_name", ""),
                "amenities": item.get("amenities", []),
            }
            roomList.append(room)

        return roomList

    def delete_room(self, building_id: str, room_id: str) -> None:
        """Delete a room."""
        self.get_room(building_id, room_id)
        self.table.delete_item(
            Key={"PK": f"BUILDING#{building_id}", "SK": f"ROOM#{room_id}"}
        )
