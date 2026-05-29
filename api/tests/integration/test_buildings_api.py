import pytest
import requests

pytestmark = pytest.mark.integration


class TestCreateBuilding:
    def test_create_building_as_admin(self, api_url, cleanup_building):
        response = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": "HQ Building",
                "address": "123 Main St",
                "num_floors": 5,
                "_user": {"is_admin": True},
            },
        )

        assert response.status_code == 201
        body = response.json()
        assert body["building"]["name"] == "HQ Building"
        assert body["building"]["num_floors"] == 5
        cleanup_building(body["building"]["building_id"])

    def test_create_building_rejected_for_non_admin(self, api_url):
        response = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": "Blocked",
                "address": "Nowhere",
                "num_floors": 2,
                "_user": {"is_admin": False},
            },
        )

        assert response.status_code == 403

    def test_create_building_invalid_floors(self, api_url):
        response = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": "Bad",
                "address": "X",
                "num_floors": 0,
                "_user": {"is_admin": True},
            },
        )

        assert response.status_code == 400


class TestListBuildings:
    def test_list_buildings(self, api_url, create_building):
        create_building("Test Building A", "Addr A", 3)
        create_building("Test Building B", "Addr B", 2)

        response = requests.get(f"{api_url}/buildings/")

        assert response.status_code == 200
        buildings = response.json()["buildings"]
        assert len(buildings) >= 2


class TestGetBuilding:
    def test_get_building(self, api_url, create_building):
        building_id = create_building("Fetchable", "456 Ave", 4)

        response = requests.get(f"{api_url}/buildings/{building_id}")

        assert response.status_code == 200
        assert response.json()["building"]["name"] == "Fetchable"

    def test_get_nonexistent_building(self, api_url):
        response = requests.get(f"{api_url}/buildings/nonexistent-id")

        assert response.status_code == 404


class TestDeleteBuilding:
    def test_delete_building_as_admin(self, api_url):
        # Create first
        resp = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": "ToDelete",
                "address": "X",
                "num_floors": 1,
                "_user": {"is_admin": True},
            },
        )
        building_id = resp.json()["building"]["building_id"]

        # Delete
        response = requests.delete(
            f"{api_url}/buildings/{building_id}",
            json={"_user": {"is_admin": True}},
        )

        assert response.status_code == 200

        # Verify gone
        get_resp = requests.get(f"{api_url}/buildings/{building_id}")
        assert get_resp.status_code == 404
