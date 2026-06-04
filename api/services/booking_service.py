from __future__ import annotations

import os
import uuid
from typing import cast, List

import boto3
from boto3.dynamodb.conditions import Key

from typings.booking import Booking, BookingItem
from typings.room import Room
from models.booking import BookRoomRequest
from models.user import AccessLevel
from services.room_service import RoomService


class BookingService:
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
        self.room_service = RoomService(table_resource=self.table)

    def book_room(self, request: BookRoomRequest, user_access_level: int) -> Booking:
        """Book a room. Checks user access level against room requirements."""
        room: Room = self.room_service.get_room(request.building_id, request.room_id)

        if user_access_level < room["min_access_level"]:
            raise ValueError(
                f"Insufficient access level. Requires {AccessLevel.name_for(room['min_access_level'])} or above"
            )

        booking_id = str(uuid.uuid4())

        booking_item: BookingItem = {
            "PK": f"BOOKING#{booking_id}",
            "SK": f"BOOKING#{booking_id}",
            "GSI1PK": f"USER#{request.user_id}",
            "GSI1SK": f"BOOKING#{request.date}#{request.start_time}",
            "booking_id": booking_id,
            "room_id": request.room_id,
            "room_name": room["name"],
            "building_name": room["building_name"],
            "floor": room["floor"],
            "user_id": request.user_id,
            "date": request.date,
            "start_time": request.start_time,
            "end_time": request.end_time,
            "purpose": request.purpose,
            "entity_type": "BOOKING",
        }

        self.table.put_item(Item=cast(dict, booking_item))

        return {
            "booking_id": booking_id,
            "room_id": request.room_id,
            "room_name": room["name"],
            "building_name": room["building_name"],
            "floor": room["floor"],
            "user_id": request.user_id,
            "date": request.date,
            "start_time": request.start_time,
            "end_time": request.end_time,
            "purpose": request.purpose,
        }

    def get_booking(self, booking_id: str) -> Booking:
        """Get a booking by ID."""
        result = self.table.get_item(
            Key={"PK": f"BOOKING#{booking_id}", "SK": f"BOOKING#{booking_id}"}
        )

        item = result.get("Item")
        if not item:
            raise ValueError("Booking not found")
        item = cast(BookingItem, item)

        return {
            "booking_id": item["booking_id"],
            "room_id": item["room_id"],
            "room_name": item["room_name"],
            "building_name": item["building_name"],
            "floor": int(item["floor"]),
            "user_id": item["user_id"],
            "date": item["date"],
            "start_time": item["start_time"],
            "end_time": item["end_time"],
            "purpose": item["purpose"],
        }

    def list_user_bookings(self, user_id: str) -> List[Booking]:
        """List all bookings for a user."""
        result = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"USER#{user_id}")
            & Key("GSI1SK").begins_with("BOOKING#"),
        )

        booking_list: List[Booking] = []
        for item in result.get("Items", []):
            item = cast(BookingItem, item)
            booking: Booking = {
                "booking_id": item["booking_id"],
                "room_id": item["room_id"],
                "room_name": item["room_name"],
                "building_name": item["building_name"],
                "floor": int(item["floor"]),
                "user_id": item["user_id"],
                "date": item["date"],
                "start_time": item["start_time"],
                "end_time": item["end_time"],
                "purpose": item["purpose"],
            }
            booking_list.append(booking)

        return booking_list

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
