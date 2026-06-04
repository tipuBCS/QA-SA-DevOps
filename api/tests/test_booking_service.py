import pytest

from services.building_service import BuildingService
from services.room_service import RoomService
from services.booking_service import BookingService
from models.building import CreateBuildingRequest
from models.room import CreateRoomRequest
from models.booking import BookRoomRequest
from models.user import AccessLevel


class TestBookRoom:
    def test_books_room_with_sufficient_access(self, dynamodb_table):
        building_service = BuildingService(table_resource=dynamodb_table)
        room_service = RoomService(table_resource=dynamodb_table)
        booking_service = BookingService(table_resource=dynamodb_table)

        building = building_service.create_building(
            CreateBuildingRequest(name="HQ", address="1", num_floors=3)
        )
        room = room_service.create_room(
            CreateRoomRequest(
                building_id=building["building_id"],
                floor=1,
                name="Huddle",
                capacity=4,
                min_access_level=AccessLevel.EMPLOYEE,
            )
        )

        booking = booking_service.book_room(
            BookRoomRequest(
                room_id=room["room_id"],
                building_id=building["building_id"],
                user_id="user-123",
                date="2026-06-01",
                start_time="09:00",
                end_time="10:00",
                purpose="Standup",
            ),
            user_access_level=AccessLevel.EMPLOYEE,
        )

        assert booking["room_name"] == "Huddle"
        assert booking["date"] == "2026-06-01"
        assert "booking_id" in booking

    def test_rejects_booking_with_insufficient_access(self, dynamodb_table):
        building_service = BuildingService(table_resource=dynamodb_table)
        room_service = RoomService(table_resource=dynamodb_table)
        booking_service = BookingService(table_resource=dynamodb_table)

        building = building_service.create_building(
            CreateBuildingRequest(name="HQ", address="1", num_floors=3)
        )
        room_service.create_room(
            CreateRoomRequest(
                building_id=building["building_id"],
                floor=1,
                name="Boardroom",
                capacity=20,
                min_access_level=AccessLevel.DIRECTOR,
            )
        )

        room = room_service.list_rooms(building["building_id"])[0]

        with pytest.raises(ValueError, match="Insufficient access level"):
            booking_service.book_room(
                BookRoomRequest(
                    room_id=room["room_id"],
                    building_id=building["building_id"],
                    user_id="user-456",
                    date="2026-06-01",
                    start_time="10:00",
                    end_time="11:00",
                    purpose="Meeting",
                ),
                user_access_level=AccessLevel.EMPLOYEE,
            )


class TestCancelBooking:
    def test_cancel_room_successfully(self, dynamodb_table):
        building_service = BuildingService(table_resource=dynamodb_table)
        room_service = RoomService(table_resource=dynamodb_table)
        booking_service = BookingService(table_resource=dynamodb_table)

        # Create a building
        building = building_service.create_building(
            CreateBuildingRequest(name="HQ", address="1", num_floors=3)
        )

        # Create a room
        room = room_service.create_room(
            CreateRoomRequest(
                building_id=building["building_id"],
                floor=1,
                name="Huddle",
                capacity=4,
                min_access_level=AccessLevel.EMPLOYEE,
            )
        )

        # Create a booking
        booking = booking_service.book_room(
            BookRoomRequest(
                room_id=room["room_id"],
                building_id=building["building_id"],
                user_id="user-456",
                date="2026-06-01",
                start_time="10:00",
                end_time="11:00",
                purpose="Meeting",
            ),
            AccessLevel.EMPLOYEE,
        )

        # Cancel booking
        booking_service.cancel_booking(booking_id=booking["booking_id"])

        # Check if booking is no longer in dynamoDB
        with pytest.raises(ValueError, match="Booking not found"):
            booking_service.get_booking(booking["booking_id"])

    def test_rejects_cancel_invalid_booking(self, dynamodb_table):
        booking_service = BookingService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="Booking not found"):
            booking_service.cancel_booking("invalid_booking_id")
