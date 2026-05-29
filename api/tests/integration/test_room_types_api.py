import pytest
import requests

pytestmark = pytest.mark.integration


class TestCreateRoomType:
    def test_create_room_type_as_admin(self, api_url, cleanup_room_type):
        response = requests.post(
            f"{api_url}/room-types/",
            json={"name": "Huddle Space", "description": "Small informal area", "_user": {"is_admin": True}},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["room_type"]["name"] == "Huddle Space"
        assert body["room_type"]["description"] == "Small informal area"
        cleanup_room_type(body["room_type"]["room_type_id"])

    def test_create_room_type_rejected_for_non_admin(self, api_url):
        response = requests.post(
            f"{api_url}/room-types/",
            json={"name": "Blocked", "_user": {"is_admin": False}},
        )

        assert response.status_code == 403

    def test_create_duplicate_room_type(self, api_url, cleanup_room_type):
        resp = requests.post(
            f"{api_url}/room-types/",
            json={"name": "Conference Room", "_user": {"is_admin": True}},
        )
        cleanup_room_type(resp.json()["room_type"]["room_type_id"])

        response = requests.post(
            f"{api_url}/room-types/",
            json={"name": "Conference Room", "_user": {"is_admin": True}},
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["error"]


class TestListRoomTypes:
    def test_list_room_types(self, api_url, create_room_type):
        create_room_type("Training Room")
        create_room_type("Phone Booth")

        response = requests.get(f"{api_url}/room-types/")

        assert response.status_code == 200
        room_types = response.json()["room_types"]
        names = [rt["name"] for rt in room_types]
        assert "Training Room" in names
        assert "Phone Booth" in names


class TestDeleteRoomType:
    def test_delete_room_type_as_admin(self, api_url):
        # Create first
        resp = requests.post(
            f"{api_url}/room-types/",
            json={"name": "ToDelete", "_user": {"is_admin": True}},
        )
        room_type_id = resp.json()["room_type"]["room_type_id"]

        # Delete
        response = requests.delete(
            f"{api_url}/room-types/{room_type_id}",
            json={"_user": {"is_admin": True}},
        )

        assert response.status_code == 200

    def test_delete_nonexistent_room_type(self, api_url):
        response = requests.delete(
            f"{api_url}/room-types/nonexistent-id",
            json={"_user": {"is_admin": True}},
        )

        assert response.status_code == 404

    def test_delete_rejected_for_non_admin(self, api_url, create_room_type):
        room_type_id = create_room_type("Protected")

        response = requests.delete(
            f"{api_url}/room-types/{room_type_id}",
            json={"_user": {"is_admin": False}},
        )

        assert response.status_code == 403
