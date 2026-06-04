import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key
from typing import cast, List

from typings.room_type import RoomType, RoomTypeItem
from models.room_type import CreateRoomTypeRequest


class RoomTypeService:
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

    def create_room_type(self, request: CreateRoomTypeRequest) -> RoomType:
        """Create a new room type. Raises ValueError if name already exists."""
        # Check for duplicate name
        existing = self.list_room_types()
        for rt in existing:
            if rt["name"].lower() == request.name.lower():
                raise ValueError(f"Room type '{request.name}' already exists")

        room_type_id = str(uuid.uuid4())

        item: RoomTypeItem = {
            "PK": f"ROOMTYPE#{room_type_id}",
            "SK": f"ROOMTYPE#{room_type_id}",
            "GSI1PK": "ROOMTYPES",
            "GSI1SK": f"ROOMTYPE#{request.name}",
            "room_type_id": room_type_id,
            "name": request.name,
            "description": request.description,
            "entity_type": "ROOMTYPE",
        }

        self.table.put_item(Item=cast(dict, item))

        return {
            "room_type_id": room_type_id,
            "name": request.name,
            "description": request.description,
        }

    def get_room_type(self, room_type_id: str) -> RoomType:
        """Get a room type by ID."""
        result = self.table.get_item(
            Key={"PK": f"ROOMTYPE#{room_type_id}", "SK": f"ROOMTYPE#{room_type_id}"}
        )
        item = result.get("Item")
        if not item:
            raise ValueError("Room type not found")
        item = cast(RoomTypeItem, item)

        return {
            "room_type_id": item["room_type_id"],
            "name": item["name"],
            "description": item["description"],
        }

    def list_room_types(self) -> List[RoomType]:
        """List all room types."""
        result = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("ROOMTYPES"),
        )

        room_type_list: List[RoomType] = []
        for item in result.get("Items", []):
            item = cast(RoomTypeItem, item)
            room_type: RoomType = {
                "room_type_id": item["room_type_id"],
                "name": item["name"],
                "description": item["description"],
            }
            room_type_list.append(room_type)

        return room_type_list

    def delete_room_type(self, room_type_id: str) -> None:
        """Delete a room type. Raises ValueError if not found."""
        self.get_room_type(room_type_id)
        self.table.delete_item(
            Key={"PK": f"ROOMTYPE#{room_type_id}", "SK": f"ROOMTYPE#{room_type_id}"}
        )
