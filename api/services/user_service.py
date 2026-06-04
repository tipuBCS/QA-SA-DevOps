import os
import uuid
import hashlib
import secrets

from aws_lambda_powertools import Logger

import boto3
from boto3.dynamodb.conditions import Key
from typing import cast, Optional

from typings.user import User, UserItem
from models.user import CreateUserRequest, LoginRequest, AccessLevel

logger = Logger()

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

    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash a password with a salt. Returns (hash, salt)."""
        if salt is None:
            salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        return hashed.hex(), salt

    def _validate_password(self, password: str) -> None:
        """Validate password meets requirements. Raises ValueError if invalid."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one number")

    def create_user(self, request: CreateUserRequest) -> User:
        """Create a new user. Raises ValueError if email already exists or password is invalid."""
        self._validate_password(request.password)

        # Check if user already exists
        existing = self.table.query(
            IndexName="GSI1",
            KeyConditionExpression=Key("GSI1PK").eq(f"EMAIL#{request.email}"),
        )
        if existing.get("Items"):
            raise ValueError("User with this email already exists")

        user_id = str(uuid.uuid4())
        password_hash, salt = self._hash_password(request.password)

        item: UserItem = {
            "PK": f"USER#{user_id}",
            "SK": f"USER#{user_id}",
            "GSI1PK": f"EMAIL#{request.email}",
            "GSI1SK": f"USER#{user_id}",
            "user_id": user_id,
            "email": request.email,
            "name": request.name,
            "password_hash": password_hash,
            "salt": salt,
            "is_admin": request.is_admin,
            "access_level": request.access_level,
            "entity_type": "USER",
        }

        self.table.put_item(Item=cast(dict, item))

        return {
            "user_id": user_id,
            "email": request.email,
            "name": request.name,
            "is_admin": request.is_admin,
            "access_level": request.access_level,
            "access_level_name": AccessLevel.name_for(request.access_level),
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

        user = cast(UserItem, items[0])
        password_hash, _ = self._hash_password(request.password, user["salt"])

        if password_hash != user["password_hash"]:
            raise ValueError("Invalid email or password")

        return {
            "message": "Login successful",
            "user": {
                "user_id": user["user_id"],
                "email": user["email"],
                "name": user["name"],
                "is_admin": user["is_admin"],
                "access_level": user["access_level"],
                "access_level_name": AccessLevel.name_for(user["access_level"]),
            },
        }

    def get_user(self, user_id: str) -> User:
        """Get a user by ID."""
        result = self.table.get_item(
            Key={"PK": f"USER#{user_id}", "SK": f"USER#{user_id}"}
        )

        item = result.get("Item")
        if not item:
            raise ValueError("User not found")
        item = cast(UserItem, item)

        return {
            "user_id": item["user_id"],
            "email": item["email"],
            "name": item["name"],
            "is_admin": item["is_admin"],
            "access_level": item["access_level"],
            "access_level_name": AccessLevel.name_for(item["access_level"]),
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
