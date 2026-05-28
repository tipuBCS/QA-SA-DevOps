import os
import uuid
import hashlib
import secrets

import boto3
from boto3.dynamodb.conditions import Key

from models.user import CreateUserRequest, LoginRequest


class UserService:
    def __init__(self, table_resource=None):
        """
        Accept an optional table resource for dependency injection (testing).
        If not provided, uses the real DynamoDB table from environment.
        """
        if table_resource:
            self.table = table_resource
        else:
            dynamodb = boto3.resource("dynamodb")
            table_name = os.environ.get("DB_TABLE_NAME", "room-booker")
            self.table = dynamodb.Table(table_name)

    def _hash_password(self, password: str, salt: str = None) -> tuple[str, str]:
        """Hash a password with a salt. Returns (hash, salt)."""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        return hashed.hex(), salt

    def create_user(self, request: CreateUserRequest) -> dict:
        """Create a new user. Raises ValueError if email already exists."""
        # Check if user already exists
        existing = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"EMAIL#{request.email}"),
        )
        if existing.get("Items"):
            raise ValueError("User with this email already exists")

        user_id = str(uuid.uuid4())
        password_hash, salt = self._hash_password(request.password)

        item = {
            "PK": f"USER#{user_id}",
            "SK": f"USER#{user_id}",
            "GSI1PK": f"EMAIL#{request.email}",
            "GSI1SK": f"USER#{user_id}",
            "user_id": user_id,
            "email": request.email,
            "name": request.name,
            "password_hash": password_hash,
            "salt": salt,
            "entity_type": "USER",
        }

        self.table.put_item(Item=item)

        return {
            "user_id": user_id,
            "email": request.email,
            "name": request.name,
        }

    def login(self, request: LoginRequest) -> dict:
        """Authenticate a user by email and password."""
        # Look up user by email via GSI
        result = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"EMAIL#{request.email}"),
        )

        items = result.get("Items", [])
        if not items:
            raise ValueError("Invalid email or password")

        user = items[0]
        password_hash, _ = self._hash_password(request.password, user["salt"])

        if password_hash != user["password_hash"]:
            raise ValueError("Invalid email or password")

        return {
            "message": "Login successful",
            "user": {
                "user_id": user["user_id"],
                "email": user["email"],
                "name": user["name"],
            },
        }

    def get_user(self, user_id: str) -> dict:
        """Get a user by ID."""
        result = self.table.get_item(
            Key={"PK": f"USER#{user_id}", "SK": f"USER#{user_id}"}
        )

        item = result.get("Item")
        if not item:
            raise ValueError("User not found")

        return {
            "user_id": item["user_id"],
            "email": item["email"],
            "name": item["name"],
        }

    def delete_user(self, user_id: str) -> None:
        """Delete a user by ID. Raises ValueError if user doesn't exist."""
        result = self.table.get_item(
            Key={"PK": f"USER#{user_id}", "SK": f"USER#{user_id}"}
        )

        item = result.get("Item")
        if not item:
            raise ValueError("User not found")

        self.table.delete_item(
            Key={"PK": f"USER#{user_id}", "SK": f"USER#{user_id}"}
        )
