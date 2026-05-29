import pytest
import requests

pytestmark = pytest.mark.integration


class TestSignup:
    def test_signup_returns_201(self, api_url, unique_email, cleanup):
        response = requests.post(
            f"{api_url}/users/signup",
            json={"email": unique_email, "password": "SecurePass1", "name": "New User"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["message"] == "User created successfully"
        assert body["user"]["email"] == unique_email
        assert body["user"]["name"] == "New User"
        assert "user_id" in body["user"]
        cleanup(body["user"]["user_id"])

    def test_signup_duplicate_email_returns_error(self, api_url, unique_email, create_user):
        create_user(unique_email)

        response = requests.post(
            f"{api_url}/users/signup",
            json={"email": unique_email, "password": "Other123", "name": "Duplicate"},
        )

        assert response.status_code == 409

    def test_signup_missing_fields_returns_error(self, api_url):
        response = requests.post(
            f"{api_url}/users/signup",
            json={"email": "incomplete@test.com"},
        )

        assert response.status_code in (400, 422, 500)

    def test_signup_invalid_password(self, api_url, unique_email):
        response = requests.post(
            f"{api_url}/users/signup",
            json={"email": unique_email, "password": "short", "name": "Weak Pass"},
        )

        assert response.status_code == 409
        assert "Password" in response.json()["error"]


class TestLogin:
    def test_login_with_valid_credentials(self, api_url, unique_email, create_user):
        create_user(unique_email, password="CorrectPass1")

        response = requests.post(
            f"{api_url}/users/login",
            json={"email": unique_email, "password": "CorrectPass1"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Login successful"
        assert body["user"]["email"] == unique_email

    def test_login_with_wrong_password(self, api_url, unique_email, create_user):
        create_user(unique_email, password="RightPass1")

        response = requests.post(
            f"{api_url}/users/login",
            json={"email": unique_email, "password": "WrongPass1"},
        )

        assert response.status_code == 401

    def test_login_with_nonexistent_email(self, api_url):
        response = requests.post(
            f"{api_url}/users/login",
            json={"email": "nobody@nowhere.com", "password": "whatever"},
        )

        assert response.status_code == 401


class TestGetUser:
    def test_get_user_returns_user_data(self, api_url, unique_email, create_user):
        resp = create_user(unique_email, name="Fetchable User")
        user_id = resp.json()["user"]["user_id"]

        response = requests.get(f"{api_url}/users/{user_id}")

        assert response.status_code == 200
        body = response.json()
        assert body["user"]["email"] == unique_email
        assert body["user"]["name"] == "Fetchable User"

    def test_get_user_nonexistent_returns_error(self, api_url):
        response = requests.get(f"{api_url}/users/nonexistent-id-12345")

        assert response.status_code == 404


class TestFullFlow:
    def test_signup_login_and_get_user(self, api_url, unique_email, cleanup):
        """End-to-end: signup → login → get user by ID."""
        # Signup
        signup_resp = requests.post(
            f"{api_url}/users/signup",
            json={"email": unique_email, "password": "FlowTest1", "name": "Flow User"},
        )
        assert signup_resp.status_code == 201
        user_id = signup_resp.json()["user"]["user_id"]
        cleanup(user_id)

        # Login
        login_resp = requests.post(
            f"{api_url}/users/login",
            json={"email": unique_email, "password": "FlowTest1"},
        )
        assert login_resp.status_code == 200
        assert login_resp.json()["user"]["user_id"] == user_id

        # Get user
        get_resp = requests.get(f"{api_url}/users/{user_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["user"]["email"] == unique_email
