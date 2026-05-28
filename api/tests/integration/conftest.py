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
