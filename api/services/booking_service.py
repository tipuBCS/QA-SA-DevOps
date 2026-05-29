import os
import uuid

import boto3
from boto3.dynamodb.conditions import Key

from models.booking import BookRoomRequest
from models.user import AccessLevel


class BookingService:
    def __init__(self, table_resource=None):
        if table_resource:
            self.table = table_resource
        else:
            dynamodb = boto3.resource("dynamodb")
            table_name = os.environ.get("DB_TABLE_NAME", "room-booker")
            self.table = dynamodb.Table(table_name)

    def book_room(self, request: BookRoomRequest, user_access_level: int) -> dict:
        """Book a room. Checks user access level against room requirements."""
        # Get the room to check access level
        result = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq("ROOMS"),
        )
        room = None
        for item in result.get("Items", []):
            if item["room_id"] == request.room_id:
                room = item
                break

        if not room:
            raise ValueError("Room not found")

        min_level = int(room["min_access_level"])
        if user_access_level < min_level:
            raise ValueError(
                f"Insufficient access level. Requires {AccessLevel.name_for(min_level)} or above"
            )

        booking_id = str(uuid.uuid4())

        item = {
            "PK": f"BOOKING#{booking_id}",
            "SK": f"BOOKING#{booking_id}",
            "GSI1PK": f"USER#{request.user_id}",
            "GSI1SK": f"BOOKING#{request.date}#{request.start_time}",
            "booking_id": booking_id,
            "room_id": request.room_id,
            "room_name": room["name"],
            "building_name": room["building_name"],
            "floor": int(room["floor"]),
            "user_id": request.user_id,
            "date": request.date,
            "start_time": request.start_time,
            "end_time": request.end_time,
            "purpose": request.purpose,
            "entity_type": "BOOKING",
        }

        self.table.put_item(Item=item)

        return {
            "booking_id": booking_id,
            "room_id": request.room_id,
            "room_name": room["name"],
            "building_name": room["building_name"],
            "floor": int(room["floor"]),
            "date": request.date,
            "start_time": request.start_time,
            "end_time": request.end_time,
            "purpose": request.purpose,
        }

    def list_user_bookings(self, user_id: str) -> list:
        """List all bookings for a user."""
        result = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"USER#{user_id}")
            & Key("GSI1SK").begins_with("BOOKING#"),
        )
        return [
            {
                "booking_id": item["booking_id"],
                "room_id": item["room_id"],
                "room_name": item["room_name"],
                "building_name": item["building_name"],
                "floor": int(item["floor"]),
                "date": item["date"],
                "start_time": item["start_time"],
                "end_time": item["end_time"],
                "purpose": item["purpose"],
            }
            for item in result.get("Items", [])
        ]

    def cancel_booking(self, booking_id: str) -> None:
        """Cancel a booking."""
        result = self.table.get_item(
            Key={"PK": f"BOOKING#{booking_id}", "SK": f"BOOKING#{booking_id}"}
        )
        if not result.get("Item"):
            raise ValueError("Booking not found")

        self.table.delete_item(
            Key={"PK": f"BOOKING#{booking_id}", "SK": f"BOOKING#{booking_id}"}
        )
