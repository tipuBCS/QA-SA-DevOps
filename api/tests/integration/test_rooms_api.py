import pytest
import requests

pytestmark = pytest.mark.integration


class TestCreateRoom:
    def test_create_room_as_admin(self, api_url, admin_headers, create_building, cleanup_room):
        building_id = create_building("Room Test HQ", "123", 5)

        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 3,
                "name": "Conference A",
                "capacity": 10,
                "min_access_level": 1,
                "amenities": ["Projector", "Whiteboard"],
            },
            headers=admin_headers,
        )

        assert response.status_code == 201
        body = response.json()
        assert body["room"]["name"] == "Conference A"
        assert body["room"]["floor"] == 3
        assert body["room"]["min_access_level"] == 1
        cleanup_room(building_id, body["room"]["room_id"])

    def test_create_room_rejected_for_non_admin(self, api_url, user_headers, create_building):
        building_id = create_building("No Admin", "X", 3)

        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 1,
                "name": "Blocked",
                "capacity": 4,
                "min_access_level": 1,
            },
            headers=user_headers,
        )

        assert response.status_code == 403

    def test_create_room_rejected_without_token(self, api_url, create_building):
        building_id = create_building("No Auth", "X", 3)

        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 1,
                "name": "No Token",
                "capacity": 4,
                "min_access_level": 1,
            },
        )

        assert response.status_code == 401

    def test_create_room_invalid_floor(self, api_url, admin_headers, create_building):
        building_id = create_building("Small", "X", 2)

        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": 10,
                "name": "Bad Floor",
                "capacity": 4,
                "min_access_level": 1,
            },
            headers=admin_headers,
        )

        assert response.status_code == 400
        assert "Floor" in response.json()["error"]


class TestListRooms:
    def test_list_rooms_for_building(self, api_url, admin_headers, create_building, create_room):
        building_id = create_building("List Rooms HQ", "123", 3)

        create_room(building_id, floor=1, name="Room A", capacity=4, min_access_level=1)
        create_room(building_id, floor=2, name="Room B", capacity=8, min_access_level=2)

        response = requests.get(
            f"{api_url}/buildings/{building_id}/rooms",
            headers=admin_headers,
        )

        assert response.status_code == 200
        rooms = response.json()["rooms"]
        assert len(rooms) == 2
        names = [r["name"] for r in rooms]
        assert "Room A" in names
        assert "Room B" in names


class TestGetRoom:
    def test_get_room(self, api_url, user_headers, create_building, create_room):
        building_id = create_building("Get Room HQ", "123", 3)
        room_id = create_room(building_id, floor=2, name="Fetchable Room", capacity=6)

        response = requests.get(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}",
            headers=user_headers,
        )

        assert response.status_code == 200
        assert response.json()["room"]["name"] == "Fetchable Room"

    def test_get_room_without_token_returns_401(self, api_url, create_building, create_room):
        building_id = create_building("Auth Room", "X", 2)
        room_id = create_room(building_id, floor=1, name="Protected")

        response = requests.get(f"{api_url}/buildings/{building_id}/rooms/{room_id}")

        assert response.status_code == 401

    def test_get_nonexistent_room(self, api_url, admin_headers, create_building):
        building_id = create_building("Empty", "X", 1)

        response = requests.get(
            f"{api_url}/buildings/{building_id}/rooms/nonexistent",
            headers=admin_headers,
        )

        assert response.status_code == 404


class TestDeleteRoom:
    def test_delete_room_as_admin(self, api_url, admin_headers, create_building, create_room):
        building_id = create_building("Delete Room HQ", "X", 3)
        room_id = create_room(building_id, floor=1, name="ToDelete")

        response = requests.delete(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}",
            headers=admin_headers,
        )

        assert response.status_code == 200

        # Verify gone
        get_resp = requests.get(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}",
            headers=admin_headers,
        )
        assert get_resp.status_code == 404

    def test_delete_room_rejected_for_non_admin(self, api_url, user_headers, create_building, create_room):
        building_id = create_building("No Delete", "Y", 2)
        room_id = create_room(building_id, floor=1, name="CantDelete")

        response = requests.delete(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}",
            headers=user_headers,
        )

        assert response.status_code == 403

    def test_delete_room_rejected_without_token(self, api_url, create_building, create_room):
        building_id = create_building("No Auth Delete", "Z", 2)
        room_id = create_room(building_id, floor=1, name="NoToken")

        response = requests.delete(f"{api_url}/buildings/{building_id}/rooms/{room_id}")

        assert response.status_code == 401
