"""
Seed an admin user into DynamoDB.

Usage:
    uv run python scripts/seed_admin.py

Reads configuration from .env:
    - TEST_ADMIN_EMAIL
    - TEST_ADMIN_PASSWORD
    - DB_TABLE_NAME (optional, defaults to "room-booker-dev")

Requires AWS credentials to be configured (e.g. via AWS_PROFILE).
"""

import os
import sys
from pathlib import Path

# Add the api directory to the path so we can import services
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load .env
env_file = Path(__file__).resolve().parent.parent / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

from models.user import CreateUserRequest
from services.user_service import UserService


def seed_admin():
    email = os.environ.get("TEST_ADMIN_EMAIL")
    password = os.environ.get("TEST_ADMIN_PASSWORD")
    table_name = os.environ.get("DB_TABLE_NAME", "room-booker-dev")

    if not email or not password:
        print("ERROR: TEST_ADMIN_EMAIL and TEST_ADMIN_PASSWORD must be set in .env")
        sys.exit(1)

    print(f"Seeding admin user: {email}")
    print(f"Table: {table_name}")

    os.environ["DB_TABLE_NAME"] = table_name

    # Ensure region is set
    region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION", "eu-west-2"))
    os.environ["AWS_DEFAULT_REGION"] = region

    service = UserService()

    request = CreateUserRequest(
        email=email,
        password=password,
        name="Admin",
        is_admin=True,
        access_level=4,
    )

    try:
        user = service.create_user(request)
        print(f"Admin user created successfully!")
        print(f"  user_id: {user['user_id']}")
        print(f"  email: {user['email']}")
        print(f"  is_admin: {user['is_admin']}")
        print(f"  access_level: {user['access_level']}")
    except ValueError as e:
        if "already exists" in str(e):
            print(f"Admin user already exists — skipping.")
        else:
            print(f"ERROR: {e}")
            sys.exit(1)


if __name__ == "__main__":
    seed_admin()
