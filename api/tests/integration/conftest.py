import os
import uuid
from pathlib import Path

import pytest
import requests

# Load .env file from the api directory
env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


@pytest.fixture(scope="session")
def api_url():
    """Get the API URL from environment variable."""
    url = os.environ.get("API_URL")
    if not url:
        pytest.skip("API_URL environment variable not set")
    return url.rstrip("/")


@pytest.fixture
def unique_email():
    """Generate a unique email for each test to avoid conflicts."""
    return f"test-{uuid.uuid4().hex[:8]}@integration-test.com"


@pytest.fixture
def cleanup(api_url):
    """Tracks user IDs and deletes them after the test."""
    user_ids = []

    def _track(user_id: str):
        user_ids.append(user_id)

    yield _track

    for user_id in user_ids:
        requests.delete(f"{api_url}/users/{user_id}")


@pytest.fixture
def create_user(api_url, cleanup):
    """Helper fixture to create a user and return the response."""

    def _create(email: str, password: str = "TestPass123", name: str = "Test User"):
        response = requests.post(
            f"{api_url}/users/signup",
            json={"email": email, "password": password, "name": name},
        )
        if response.status_code == 201:
            user_id = response.json()["user"]["user_id"]
            cleanup(user_id)
        return response

    return _create


@pytest.fixture
def cleanup_building(api_url):
    """Tracks building IDs and deletes them after the test."""
    building_ids = []

    def _track(building_id: str):
        building_ids.append(building_id)

    yield _track

    for building_id in building_ids:
        requests.delete(
            f"{api_url}/buildings/{building_id}",
            json={"_user": {"is_admin": True}},
        )


@pytest.fixture
def cleanup_room(api_url):
    """Tracks room IDs and deletes them after the test."""
    rooms = []

    def _track(building_id: str, room_id: str):
        rooms.append((building_id, room_id))

    yield _track

    for building_id, room_id in rooms:
        requests.delete(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}",
            json={"_user": {"is_admin": True}},
        )


@pytest.fixture
def create_building(api_url, cleanup_building):
    """Helper fixture to create a building and return the building_id."""

    def _create(name: str, address: str, num_floors: int):
        response = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": name,
                "address": address,
                "num_floors": num_floors,
                "_user": {"is_admin": True},
            },
        )
        building_id = response.json()["building"]["building_id"]
        cleanup_building(building_id)
        return building_id

    return _create


@pytest.fixture
def cleanup_room_type(api_url):
    """Tracks room type IDs and deletes them after the test."""
    room_type_ids = []

    def _track(room_type_id: str):
        room_type_ids.append(room_type_id)

    yield _track

    for room_type_id in room_type_ids:
        requests.delete(
            f"{api_url}/room-types/{room_type_id}",
            json={"_user": {"is_admin": True}},
        )


@pytest.fixture
def create_room_type(api_url, cleanup_room_type):
    """Helper fixture to create a room type and return the room_type_id."""

    def _create(name: str, description: str = ""):
        response = requests.post(
            f"{api_url}/room-types/",
            json={"name": name, "description": description, "_user": {"is_admin": True}},
        )
        room_type_id = response.json()["room_type"]["room_type_id"]
        cleanup_room_type(room_type_id)
        return room_type_id

    return _create
