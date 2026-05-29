import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key

from models.room_type import CreateRoomTypeRequest


class RoomTypeService:
    def __init__(self, table_resource=None):
        if table_resource:
            self.table = table_resource
        else:
            dynamodb = boto3.resource("dynamodb")
            table_name = os.environ.get("DB_TABLE_NAME", "room-booker")
            self.table = dynamodb.Table(table_name)

    def create_room_type(self, request: CreateRoomTypeRequest) -> dict:
        """Create a new room type. Raises ValueError if name already exists."""
        # Check for duplicate name
        existing = self.list_room_types()
        for rt in existing:
            if rt["name"].lower() == request.name.lower():
                raise ValueError(f"Room type '{request.name}' already exists")

        room_type_id = str(uuid.uuid4())

        item = {
            "PK": f"ROOMTYPE#{room_type_id}",
            "SK": f"ROOMTYPE#{room_type_id}",
            "GSI1PK": "ROOMTYPES",
            "GSI1SK": f"ROOMTYPE#{request.name}",
            "room_type_id": room_type_id,
            "name": request.name,
            "description": request.description,
            "entity_type": "ROOMTYPE",
        }

        self.table.put_item(Item=item)

        return {
            "room_type_id": room_type_id,
            "name": request.name,
            "description": request.description,
        }

    def get_room_type(self, room_type_id: str) -> dict:
        """Get a room type by ID."""
        result = self.table.get_item(
            Key={"PK": f"ROOMTYPE#{room_type_id}", "SK": f"ROOMTYPE#{room_type_id}"}
        )
        item = result.get("Item")
        if not item:
            raise ValueError("Room type not found")

        return {
            "room_type_id": item["room_type_id"],
            "name": item["name"],
            "description": item.get("description", ""),
        }

    def list_room_types(self) -> list:
        """List all room types."""
        result = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("ROOMTYPES"),
        )
        return [
            {
                "room_type_id": item["room_type_id"],
                "name": item["name"],
                "description": item.get("description", ""),
            }
            for item in result.get("Items", [])
        ]

    def delete_room_type(self, room_type_id: str) -> None:
        """Delete a room type. Raises ValueError if not found."""
        self.get_room_type(room_type_id)
        self.table.delete_item(
            Key={"PK": f"ROOMTYPE#{room_type_id}", "SK": f"ROOMTYPE#{room_type_id}"}
        )
