import pytest

from services.user_service import UserService
from models.user import CreateUserRequest, LoginRequest

pytestmark = pytest.mark.unit

# Valid test password that meets all requirements (8+ chars, upper, lower, number, special)
VALID_PASSWORD = "Secure123!"


class TestCreateUser:
    def test_creates_user_successfully(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        request = CreateUserRequest(
            email="alice@example.com", password=VALID_PASSWORD, name="Alice Test"
        )

        result = service.create_user(request)

        assert result["email"] == "alice@example.com"
        assert result["name"] == "Alice Test"
        assert "user_id" in result

    def test_stores_user_in_dynamodb(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        request = CreateUserRequest(
            email="bob@example.com", password=VALID_PASSWORD, name="Bob Smith"
        )

        result = service.create_user(request)

        # Verify it's in the table
        item = dynamodb_table.get_item(
            Key={"PK": f"USER#{result['user_id']}", "SK": f"USER#{result['user_id']}"}
        )
        assert item["Item"]["email"] == "bob@example.com"
        assert item["Item"]["name"] == "Bob Smith"
        assert item["Item"]["entity_type"] == "USER"

    def test_does_not_store_plain_password(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        request = CreateUserRequest(
            email="carol@example.com", password=VALID_PASSWORD, name="Carol Jones"
        )

        result = service.create_user(request)

        item = dynamodb_table.get_item(
            Key={"PK": f"USER#{result['user_id']}", "SK": f"USER#{result['user_id']}"}
        )
        assert "password" not in item["Item"]
        assert item["Item"]["password_hash"] != VALID_PASSWORD

    def test_raises_error_for_duplicate_email(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        request = CreateUserRequest(
            email="dupe@example.com", password=VALID_PASSWORD, name="First User"
        )
        service.create_user(request)

        with pytest.raises(ValueError, match="already exists"):
            service.create_user(
                CreateUserRequest(
                    email="dupe@example.com", password=VALID_PASSWORD, name="Second User"
                )
            )

    def test_raises_error_for_short_password(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="at least 8 characters"):
            service.create_user(
                CreateUserRequest(email="short@example.com", password="Ab1!", name="Short Test")
            )

    def test_raises_error_for_password_without_uppercase(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="uppercase"):
            service.create_user(
                CreateUserRequest(email="noup@example.com", password="lowercase1!", name="No Upper")
            )

    def test_raises_error_for_password_without_lowercase(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="lowercase"):
            service.create_user(
                CreateUserRequest(email="nolow@example.com", password="UPPERCASE1!", name="No Lower")
            )

    def test_raises_error_for_password_without_number(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="number"):
            service.create_user(
                CreateUserRequest(email="nonum@example.com", password="NoNumbers!", name="No Number")
            )

    def test_raises_error_for_password_without_special_character(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="special character"):
            service.create_user(
                CreateUserRequest(email="nospec@example.com", password="NoSpecial1", name="No Special")
            )

    def test_raises_error_for_invalid_email_format(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="Invalid email format"):
            service.create_user(
                CreateUserRequest(email="notanemail", password=VALID_PASSWORD, name="Bad Email")
            )

    def test_raises_error_for_email_without_domain(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="Invalid email format"):
            service.create_user(
                CreateUserRequest(email="user@domain", password=VALID_PASSWORD, name="Bad Domain")
            )

    def test_raises_error_for_short_name(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="at least 3 characters"):
            service.create_user(
                CreateUserRequest(email="short@example.com", password=VALID_PASSWORD, name="AB")
            )

    def test_raises_error_for_name_with_numbers(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="only letters and spaces"):
            service.create_user(
                CreateUserRequest(email="num@example.com", password=VALID_PASSWORD, name="User123")
            )


class TestLogin:
    def test_login_successful_with_correct_credentials(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        service.create_user(
            CreateUserRequest(email="user@example.com", password=VALID_PASSWORD, name="Test User")
        )

        result = service.login(LoginRequest(email="user@example.com", password=VALID_PASSWORD))

        assert result["message"] == "Login successful"
        assert result["user"]["email"] == "user@example.com"
        assert isinstance(result["token"], str)
        assert len(result["token"]) > 0

    def test_login_fails_with_wrong_password(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        service.create_user(
            CreateUserRequest(email="user@example.com", password=VALID_PASSWORD, name="Test User")
        )

        with pytest.raises(ValueError, match="Invalid email or password"):
            service.login(LoginRequest(email="user@example.com", password="WrongPass1!"))

    def test_login_fails_with_nonexistent_email(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="Invalid email or password"):
            service.login(LoginRequest(email="nobody@example.com", password=VALID_PASSWORD))


class TestGetUser:
    def test_get_user_returns_user_data(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        created = service.create_user(
            CreateUserRequest(email="get@example.com", password=VALID_PASSWORD, name="Get User")
        )

        result = service.get_user(created["user_id"])

        assert result["email"] == "get@example.com"
        assert result["name"] == "Get User"
        assert result["user_id"] == created["user_id"]

    def test_get_user_does_not_return_password(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)
        created = service.create_user(
            CreateUserRequest(email="safe@example.com", password=VALID_PASSWORD, name="Safe User")
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
            CreateUserRequest(email="delete@example.com", password=VALID_PASSWORD, name="Delete User")
        )

        service.delete_user(created["user_id"])

        with pytest.raises(ValueError, match="User not found"):
            service.get_user(created["user_id"])

    def test_delete_user_raises_for_nonexistent_id(self, dynamodb_table):
        service = UserService(table_resource=dynamodb_table)

        with pytest.raises(ValueError, match="User not found"):
            service.delete_user("nonexistent-id")
