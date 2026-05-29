import pytest

from services.user_service import UserService
from models.user import CreateUserRequest, LoginRequest


class TestCreateUser:
    def test_creates_user_successfully(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        request = CreateUserRequest(
            email="alice@example.com", password="Secure123", name="Alice"
        )

        result = service.create_user(request)

        assert result["email"] == "alice@example.com"
        assert result["name"] == "Alice"
        assert "user_id" in result

    def test_stores_user_in_dynamodb(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        request = CreateUserRequest(
            email="bob@example.com", password="Password123", name="Bob"
        )

        result = service.create_user(request)

        # Verify it's in the table
        item = dynamodb_table.get_item(
            Key={"PK": f"USER#{result['user_id']}", "SK": f"USER#{result['user_id']}"}
        )
        assert item["Item"]["email"] == "bob@example.com"
        assert item["Item"]["name"] == "Bob"
        assert item["Item"]["entity_type"] == "USER"

    def test_does_not_store_plain_password(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        request = CreateUserRequest(
            email="carol@example.com", password="MyPassword1", name="Carol"
        )

        result = service.create_user(request)

        item = dynamodb_table.get_item(
            Key={"PK": f"USER#{result['user_id']}", "SK": f"USER#{result['user_id']}"}
        )
        assert "password" not in item["Item"]
        assert item["Item"]["password_hash"] != "mypassword"

    def test_raises_error_for_duplicate_email(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        request = CreateUserRequest(
            email="dupe@example.com", password="Pass1234", name="First"
        )
        service.create_user(request)

        with pytest.raises(ValueError, match="already exists"):
            service.create_user(
                CreateUserRequest(
                    email="dupe@example.com", password="Other123", name="Second"
                )
            )

    def test_raises_error_for_short_password(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="at least 8 characters"):
            service.create_user(
                CreateUserRequest(email="short@example.com", password="Ab1", name="Short")
            )

    def test_raises_error_for_password_without_uppercase(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="uppercase"):
            service.create_user(
                CreateUserRequest(email="noup@example.com", password="lowercase1", name="NoUp")
            )

    def test_raises_error_for_password_without_lowercase(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="lowercase"):
            service.create_user(
                CreateUserRequest(email="nolow@example.com", password="UPPERCASE1", name="NoLow")
            )

    def test_raises_error_for_password_without_number(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="number"):
            service.create_user(
                CreateUserRequest(email="nonum@example.com", password="NoNumbers", name="NoNum")
            )


class TestLogin:
    def test_login_successful_with_correct_credentials(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        service.create_user(
            CreateUserRequest(email="user@example.com", password="Correct1x", name="User")
        )

        result = service.login(LoginRequest(email="user@example.com", password="Correct1x"))

        assert result["message"] == "Login successful"
        assert result["user"]["email"] == "user@example.com"

    def test_login_fails_with_wrong_password(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        service.create_user(
            CreateUserRequest(email="user@example.com", password="Correct1x", name="User")
        )

        with pytest.raises(ValueError, match="Invalid email or password"):
            service.login(LoginRequest(email="user@example.com", password="WrongPass1"))

    def test_login_fails_with_nonexistent_email(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="Invalid email or password"):
            service.login(LoginRequest(email="nobody@example.com", password="ValidPass1"))


class TestGetUser:
    def test_get_user_returns_user_data(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        created = service.create_user(
            CreateUserRequest(email="get@example.com", password="ValidPass1", name="GetMe")
        )

        result = service.get_user(created["user_id"])

        assert result["email"] == "get@example.com"
        assert result["name"] == "GetMe"
        assert result["user_id"] == created["user_id"]

    def test_get_user_does_not_return_password(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        created = service.create_user(
            CreateUserRequest(email="safe@example.com", password="Secret123", name="Safe")
        )

        result = service.get_user(created["user_id"])

        assert "password_hash" not in result
        assert "salt" not in result
        assert "password" not in result

    def test_get_user_raises_for_nonexistent_id(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="User not found"):
            service.get_user("nonexistent-id")


class TestDeleteUser:
    def test_delete_user_removes_from_table(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        created = service.create_user(
            CreateUserRequest(email="delete@example.com", password="ValidPass1", name="DeleteMe")
        )

        service.delete_user(created["user_id"])

        with pytest.raises(ValueError, match="User not found"):
            service.get_user(created["user_id"])

    def test_delete_user_raises_for_nonexistent_id(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="User not found"):
            service.delete_user("nonexistent-id")
