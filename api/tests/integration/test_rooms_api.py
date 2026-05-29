import pytest
import requests

pytestmark = pytest.mark.integration


class TestCreateRoom:
    def test_create_room_as_admin(self, api_url, create_building, cleanup_room):
        building_id = create_building("Room Test HQ", "123", 5)

        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 3,
                "name": "Conference A",
                "capacity": 10,
                "min_access_level": 1,
                "amenities": ["Projector", "Whiteboard"],
                "_user": {"is_admin": True},
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["room"]["name"] == "Conference A"
        assert body["room"]["floor"] == 3
        assert body["room"]["min_access_level"] == 1
        cleanup_room(building_id, body["room"]["room_id"])

    def test_create_room_rejected_for_non_admin(self, api_url, create_building):
        building_id = create_building("No Admin", "X", 3)

        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 1,
                "name": "Blocked",
                "capacity": 4,
                "min_access_level": 1,
                "_user": {"is_admin": False},
            },
        )

        assert response.status_code == 403

    def test_create_room_invalid_floor(self, api_url, create_building):
        building_id = create_building("Small", "X", 2)

        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 10,
                "name": "Bad Floor",
                "capacity": 4,
                "min_access_level": 1,
                "_user": {"is_admin": True},
            },
        )

        assert response.status_code == 400
        assert "Floor" in response.json()["error"]


class TestListRooms:
    def test_list_rooms_for_building(self, api_url, create_building, cleanup_room):
        building_id = create_building("List Rooms HQ", "123", 3)

        # Create two rooms
        resp1 = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={"floor": 1, "name": "Room A", "capacity": 4, "min_access_level": 1, "_user": {"is_admin": True}},
        )
        resp2 = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={"floor": 2, "name": "Room B", "capacity": 8, "min_access_level": 2, "_user": {"is_admin": True}},
        )
        cleanup_room(building_id, resp1.json()["room"]["room_id"])
        cleanup_room(building_id, resp2.json()["room"]["room_id"])

        response = requests.get(f"{api_url}/buildings/{building_id}/rooms")

        assert response.status_code == 200
        rooms = response.json()["rooms"]
        assert len(rooms) == 2
        names = [r["name"] for r in rooms]
        assert "Room A" in names
        assert "Room B" in names


class TestGetRoom:
    def test_get_room(self, api_url, create_building, cleanup_room):
        building_id = create_building("Get Room HQ", "123", 3)

        resp = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={"floor": 2, "name": "Fetchable Room", "capacity": 6, "min_access_level": 1, "_user": {"is_admin": True}},
        )
        room_id = resp.json()["room"]["room_id"]
        cleanup_room(building_id, room_id)

        response = requests.get(f"{api_url}/buildings/{building_id}/rooms/{room_id}")

        assert response.status_code == 200
        assert response.json()["room"]["name"] == "Fetchable Room"

    def test_get_nonexistent_room(self, api_url, create_building):
        building_id = create_building("Empty", "X", 1)

        response = requests.get(f"{api_url}/buildings/{building_id}/rooms/nonexistent")

        assert response.status_code == 404
