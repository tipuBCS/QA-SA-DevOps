import pytest
import requests

pytestmark = pytest.mark.integration


class TestCreateBuilding:
    def test_create_building_as_admin(self, api_url, admin_headers, cleanup_building):
        response = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": "HQ Building",
                "address": "123 Main St",
                "num_floors": 5,
            },
            headers=admin_headers,
        )

        assert response.status_code == 201
        body = response.json()
        assert body["building"]["name"] == "HQ Building"
        assert body["building"]["num_floors"] == 5
        cleanup_building(body["building"]["building_id"])

    def test_create_building_rejected_for_non_admin(self, api_url, user_headers):
        response = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": "Blocked",
                "address": "Nowhere",
                "num_floors": 2,
            },
            headers=user_headers,
        )

        assert response.status_code == 403

    def test_create_building_rejected_without_token(self, api_url):
        response = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": "No Auth",
                "address": "Nowhere",
                "num_floors": 2,
            },
        )

        assert response.status_code == 401

    def test_create_building_invalid_floors(self, api_url, admin_headers):
        response = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": "Bad",
                "address": "X",
                "num_floors": 0,
            },
            headers=admin_headers,
        )

        assert response.status_code == 400


class TestListBuildings:
    def test_list_buildings(self, api_url, admin_headers, create_building):
        create_building("Test Building A", "Addr A", 3)
        create_building("Test Building B", "Addr B", 2)

        response = requests.get(f"{api_url}/buildings/", headers=admin_headers)

        assert response.status_code == 200
        buildings = response.json()["buildings"]
        assert len(buildings) >= 2


class TestGetBuilding:
    def test_get_building_as_authenticated_user(self, api_url, user_headers, create_building):
        building_id = create_building("Fetchable", "456 Ave", 4)

        response = requests.get(
            f"{api_url}/buildings/{building_id}",
            headers=user_headers,
        )

        assert response.status_code == 200
        assert response.json()["building"]["name"] == "Fetchable"

    def test_get_building_without_token_returns_401(self, api_url, create_building):
        building_id = create_building("Auth Required", "789 St", 2)

        response = requests.get(f"{api_url}/buildings/{building_id}")

        assert response.status_code == 401

    def test_get_nonexistent_building(self, api_url, admin_headers):
        response = requests.get(
            f"{api_url}/buildings/nonexistent-id",
            headers=admin_headers,
        )

        assert response.status_code == 404


class TestDeleteBuilding:
    def test_delete_building_as_admin(self, api_url, admin_headers, create_building):
        building_id = create_building("ToDelete", "X", 1)

        response = requests.delete(
            f"{api_url}/buildings/{building_id}",
            headers=admin_headers,
        )

        assert response.status_code == 200

        # Verify gone
        get_resp = requests.get(
            f"{api_url}/buildings/{building_id}",
            headers=admin_headers,
        )
        assert get_resp.status_code == 404

    def test_delete_building_rejected_for_non_admin(self, api_url, user_headers, create_building):
        building_id = create_building("CantDelete", "Y", 1)

        response = requests.delete(
            f"{api_url}/buildings/{building_id}",
            headers=user_headers,
        )

        assert response.status_code == 403

    def test_delete_building_rejected_without_token(self, api_url, create_building):
        building_id = create_building("NoAuth", "Z", 1)

        response = requests.delete(f"{api_url}/buildings/{building_id}")

        assert response.status_code == 401
