import pytest
import requests

pytestmark = pytest.mark.integration


class TestBookRoom:
    def test_book_room_with_sufficient_access(
        self, api_url, create_building, cleanup_room, cleanup_booking
    ):
        building_id = create_building("Booking HQ", "123", 3)

        # Create a room with employee access
        resp = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 1,
                "name": "Huddle",
                "capacity": 4,
                "min_access_level": 1,
                "_user": {"is_admin": True},
            },
        )
        room_id = resp.json()["room"]["room_id"]
        cleanup_room(building_id, room_id)

        # Book as employee
        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}/book",
            json={
                "date": "2026-06-15",
                "start_time": "09:00",
                "end_time": "10:00",
                "purpose": "Standup",
                "_user": {"user_id": "test-user-1", "access_level": 1},
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["booking"]["room_name"] == "Huddle"
        assert body["booking"]["date"] == "2026-06-15"
        cleanup_booking(body["booking"]["booking_id"])

    def test_book_room_rejected_insufficient_access(
        self, api_url, create_building, cleanup_room
    ):
        building_id = create_building("Exec HQ", "456", 5)

        # Create a director-level room
        resp = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 5,
                "name": "Boardroom",
                "capacity": 20,
                "min_access_level": 3,
                "_user": {"is_admin": True},
            },
        )
        room_id = resp.json()["room"]["room_id"]
        cleanup_room(building_id, room_id)

        # Try to book as employee
        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}/book",
            json={
                "date": "2026-06-15",
                "start_time": "10:00",
                "end_time": "11:00",
                "purpose": "Meeting",
                "_user": {"user_id": "test-user-2", "access_level": 1},
            },
        )

        assert response.status_code == 403
        assert "Insufficient access level" in response.json()["error"]

    def test_book_room_requires_authentication(
        self, api_url, create_building, cleanup_room
    ):
        building_id = create_building("Auth HQ", "789", 2)

        resp = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 1,
                "name": "Open Room",
                "capacity": 6,
                "min_access_level": 1,
                "_user": {"is_admin": True},
            },
        )
        room_id = resp.json()["room"]["room_id"]
        cleanup_room(building_id, room_id)

        # Try to book without user
        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}/book",
            json={
                "date": "2026-06-15",
                "start_time": "14:00",
                "end_time": "15:00",
                "purpose": "Test",
                "_user": {},
            },
        )

        assert response.status_code == 401


class TestCancelBooking:
    def test_cancel_booking_with_sufficient_access(
        self, api_url, create_building, create_room, create_booking
    ):
        building_id = create_building(num_floors=3)
        room_id = create_room(building_id)
        booking_id = create_booking(building_id, room_id)
        
        # Cancel Booking
        response = requests.delete(
            f"{api_url}/bookings/{booking_id}",
            json={"_user": {"is_admin": True}},
        )
        print(response.json())
        assert(response.status_code == 200)
        assert "cancelled" in response.json()["message"].lower()

    # TODO: Tests Cancel booking returns successful if owner of booking and not admin

    # TODO: Tests Cancel booking returns value error for invalid booking

    # TODO:  Tests Cancel booking returns unauthorised error for non-admin and not owner


class TestFullBookingFlow:
    def test_create_building_room_and_book(
        self, api_url, cleanup_building, cleanup_room, cleanup_booking
    ):
        """End-to-end: create building → create room → book room."""
        # Create building
        building_resp = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": "Flow HQ",
                "address": "Flow St",
                "num_floors": 3,
                "_user": {"is_admin": True},
            },
        )
        assert building_resp.status_code == 201
        building_id = building_resp.json()["building"]["building_id"]
        cleanup_building(building_id)

        # Create room
        room_resp = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 2,
                "name": "Flow Room",
                "capacity": 8,
                "min_access_level": 2,
                "_user": {"is_admin": True},
            },
        )
        assert room_resp.status_code == 201
        room_id = room_resp.json()["room"]["room_id"]
        cleanup_room(building_id, room_id)

        # Book as manager (level 2)
        book_resp = requests.post(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}/book",
            json={
                "date": "2026-07-01",
                "start_time": "11:00",
                "end_time": "12:00",
                "purpose": "Team sync",
                "_user": {"user_id": "manager-1", "access_level": 2},
            },
        )
        assert book_resp.status_code == 201
        assert book_resp.json()["booking"]["room_name"] == "Flow Room"
        cleanup_booking(book_resp.json()["booking"]["booking_id"])
