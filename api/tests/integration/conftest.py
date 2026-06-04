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


@pytest.fixture(scope="session")
def admin_token(api_url):
    """Login with the pre-seeded admin account and return the JWT token."""
    admin_email = os.environ.get("TEST_ADMIN_EMAIL")
    admin_password = os.environ.get("TEST_ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        pytest.skip("TEST_ADMIN_EMAIL and TEST_ADMIN_PASSWORD must be set in .env")

    login_response = requests.post(
        f"{api_url}/users/login",
        json={"email": admin_email, "password": admin_password},
    )
    assert login_response.status_code == 200, (
        f"Failed to login admin (is the admin user seeded?): {login_response.json()}"
    )

    return login_response.json()["token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    """Authorization headers with admin JWT token."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def unique_email():
    """Generate a unique email for each test to avoid conflicts."""
    return f"test-{uuid.uuid4().hex[:8]}@integration-test.com"


@pytest.fixture
def user_token(api_url, unique_email):
    """Create a regular user and return their JWT token."""
    requests.post(
        f"{api_url}/users/signup",
        json={
            "email": unique_email,
            "password": "TestPass123",
            "name": "Test User",
        },
    )
    login_response = requests.post(
        f"{api_url}/users/login",
        json={"email": unique_email, "password": "TestPass123"},
    )
    return login_response.json()["token"]


@pytest.fixture
def user_headers(user_token):
    """Authorization headers with regular user JWT token."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def cleanup(api_url, admin_headers):
    """Tracks user IDs and deletes them after the test."""
    user_ids = []

    def _track(user_id: str):
        user_ids.append(user_id)

    yield _track

    for user_id in user_ids:
        requests.delete(f"{api_url}/users/{user_id}", headers=admin_headers)


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
def cleanup_building(api_url, admin_headers):
    """Tracks building IDs and deletes them after the test."""
    building_ids = []

    def _track(building_id: str):
        building_ids.append(building_id)

    yield _track

    for building_id in building_ids:
        requests.delete(
            f"{api_url}/buildings/{building_id}",
            headers=admin_headers,
        )


@pytest.fixture
def cleanup_room(api_url, admin_headers):
    """Tracks room IDs and deletes them after the test."""
    rooms = []

    def _track(building_id: str, room_id: str):
        rooms.append((building_id, room_id))

    yield _track

    for building_id, room_id in rooms:
        requests.delete(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}",
            headers=admin_headers,
        )


@pytest.fixture
def create_room(api_url, admin_headers, cleanup_room):
    """Helper fixture to create a room and return the room_id."""

    def _create(
        building_id: str,
        floor: int = 2,
        name: str = "test-room",
        capacity: int = 10,
        min_access_level: int = 1,
    ):
        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms",
            json={
                "floor": floor,
                "name": name,
                "capacity": capacity,
                "min_access_level": min_access_level,
            },
            headers=admin_headers,
        )
        room_id = response.json()["room"]["room_id"]
        cleanup_room(building_id, room_id)
        return room_id

    return _create


@pytest.fixture
def create_building(api_url, admin_headers, cleanup_building):
    """Helper fixture to create a building and return the building_id."""

    def _create(name: str = "test-building", address: str = "test-address", num_floors: int = 1):
        response = requests.post(
            f"{api_url}/buildings/",
            json={
                "name": name,
                "address": address,
                "num_floors": num_floors,
            },
            headers=admin_headers,
        )
        building_id = response.json()["building"]["building_id"]
        cleanup_building(building_id)
        return building_id

    return _create


@pytest.fixture
def cleanup_room_type(api_url, admin_headers):
    """Tracks room type IDs and deletes them after the test."""
    room_type_ids = []

    def _track(room_type_id: str):
        room_type_ids.append(room_type_id)

    yield _track

    for room_type_id in room_type_ids:
        requests.delete(
            f"{api_url}/room-types/{room_type_id}",
            headers=admin_headers,
        )


@pytest.fixture
def create_room_type(api_url, admin_headers, cleanup_room_type):
    """Helper fixture to create a room type and return the room_type_id."""

    def _create(name: str, description: str = ""):
        response = requests.post(
            f"{api_url}/room-types/",
            json={
                "name": name,
                "description": description,
            },
            headers=admin_headers,
        )
        room_type_id = response.json()["room_type"]["room_type_id"]
        cleanup_room_type(room_type_id)
        return room_type_id

    return _create


@pytest.fixture
def cleanup_booking(api_url, admin_headers):
    """Tracks booking IDs and cancels them after the test."""
    booking_ids = []

    def _track(booking_id: str):
        booking_ids.append(booking_id)

    yield _track

    for booking_id in booking_ids:
        requests.delete(
            f"{api_url}/bookings/{booking_id}",
            headers=admin_headers,
        )


@pytest.fixture
def create_booking(api_url, user_headers, cleanup_booking):
    """Helper fixture to create a booking and return the booking_id."""

    def _create(building_id: str, room_id: str,
                date: str = "2026-06-15",
                start_time: str = "09:00", end_time: str = "10:00",
                purpose: str = "Test booking"):
        response = requests.post(
            f"{api_url}/buildings/{building_id}/rooms/{room_id}/book",
            json={
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "purpose": purpose,
            },
            headers=user_headers,
        )
        if response.status_code == 201:
            booking_id = response.json()["booking"]["booking_id"]
            cleanup_booking(booking_id)
            return booking_id
        raise ValueError(f"Failed to create booking: {response.status_code} - {response.json()}")

    return _create
