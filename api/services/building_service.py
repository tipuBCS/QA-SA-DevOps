import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key

from models.building import CreateBuildingRequest


class BuildingService:
    def __init__(self, table_resource=None):
        if table_resource:
            self.table = table_resource
        else:
            dynamodb = boto3.resource("dynamodb")
            table_name = os.environ.get("DB_TABLE_NAME", "room-booker")
            self.table = dynamodb.Table(table_name)

    def create_building(self, request: CreateBuildingRequest) -> dict:
        """Create a new building with a set number of floors."""
        if request.num_floors < 1:
            raise ValueError("Building must have at least 1 floor")

        building_id = str(uuid.uuid4())

        item = {
            "PK": f"BUILDING#{building_id}",
            "SK": f"BUILDING#{building_id}",
            "GSI1PK": "BUILDINGS",
            "GSI1SK": f"BUILDING#{building_id}",
            "building_id": building_id,
            "name": request.name,
            "address": request.address,
            "num_floors": request.num_floors,
            "entity_type": "BUILDING",
        }

        self.table.put_item(Item=item)

        return {
            "building_id": building_id,
            "name": request.name,
            "address": request.address,
            "num_floors": request.num_floors,
        }

    def get_building(self, building_id: str) -> dict:
        """Get a building by ID."""
        result = self.table.get_item(
            Key={"PK": f"BUILDING#{building_id}", "SK": f"BUILDING#{building_id}"}
        )
        item = result.get("Item")
        if not item:
            raise ValueError("Building not found")

        return {
            "building_id": item["building_id"],
            "name": item["name"],
            "address": item["address"],
            "num_floors": int(item["num_floors"]),
        }

    def list_buildings(self) -> list:
        """List all buildings."""
        result = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("BUILDINGS"),
        )
        return [
            {
                "building_id": item["building_id"],
                "name": item["name"],
                "address": item["address"],
                "num_floors": int(item["num_floors"]),
            }
            for item in result.get("Items", [])
        ]

    def delete_building(self, building_id: str) -> None:
        """Delete a building. Raises ValueError if not found."""
        self.get_building(building_id)
        self.table.delete_item(
            Key={"PK": f"BUILDING#{building_id}", "SK": f"BUILDING#{building_id}"}
        )
