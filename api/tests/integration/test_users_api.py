import pytest
import requests

pytestmark = pytest.mark.integration


class TestSignup:
    def test_signup_returns_201(self, api_url, unique_email, cleanup):
        response = requests.post(
            f"{api_url}/users/signup",
            json={"email": unique_email, "password": "SecurePass1!", "name": "New User"},
        )

        assert response.status_code == 201
        body = response.json()
        assert body["message"] == "User created successfully"
        assert body["user"]["email"] == unique_email
        assert body["user"]["name"] == "New User"
        assert "user_id" in body["user"]
        assert body["user"]["is_admin"] == False
        assert body["user"]["access_level"] == 1
        assert body["user"]["access_level_name"] == "Employee"

        cleanup(body["user"]["user_id"])

    def test_signup_duplicate_email_returns_error(self, api_url, unique_email, create_user):
        create_user(unique_email)

        response = requests.post(
            f"{api_url}/users/signup",
            json={"email": unique_email, "password": "Other123!", "name": "Duplicate"},
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

    def test_signup_invalid_email_format(self, api_url):
        response = requests.post(
            f"{api_url}/users/signup",
            json={"email": "notanemail", "password": "SecurePass1!", "name": "Bad Email"},
        )

        assert response.status_code == 409
        assert "email" in response.json()["error"].lower()

    def test_signup_invalid_name(self, api_url, unique_email):
        response = requests.post(
            f"{api_url}/users/signup",
            json={"email": unique_email, "password": "SecurePass1!", "name": "AB"},
        )

        assert response.status_code == 409
        assert "Name" in response.json()["error"]


class TestLogin:
    def test_login_with_valid_credentials(self, api_url, unique_email, create_user):
        create_user(unique_email, password="CorrectPass1!")

        response = requests.post(
            f"{api_url}/users/login",
            json={"email": unique_email, "password": "CorrectPass1!"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["message"] == "Login successful"
        assert body["user"]["email"] == unique_email
        assert body["user"]["is_admin"] == False
        assert body["user"]["access_level"] == 1
        assert body["user"]["access_level_name"] == "Employee"
        assert len(body["token"]) > 0

    def test_login_with_wrong_password(self, api_url, unique_email, create_user):
        create_user(unique_email, password="RightPass1!")

        response = requests.post(
            f"{api_url}/users/login",
            json={"email": unique_email, "password": "WrongPass1!"},
        )

        assert response.status_code == 401

    def test_login_with_nonexistent_email(self, api_url):
        response = requests.post(
            f"{api_url}/users/login",
            json={"email": "nobody@nowhere.com", "password": "whatever"},
        )

        assert response.status_code == 401


class TestGetUser:
    def test_get_user_returns_user_data(self, api_url, admin_headers, unique_email, create_user):
        resp = create_user(unique_email, name="Fetchable User")
        user_id = resp.json()["user"]["user_id"]

        response = requests.get(f"{api_url}/users/{user_id}", headers=admin_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["user"]["email"] == unique_email
        assert body["user"]["name"] == "Fetchable User"
        assert body["user"]["is_admin"] == False
        assert body["user"]["access_level"] == 1
        assert body["user"]["access_level_name"] == "Employee"

    def test_get_user_nonexistent_returns_error(self, api_url, admin_headers):
        response = requests.get(f"{api_url}/users/nonexistent-id-12345", headers=admin_headers)

        assert response.status_code == 404

    def test_get_user_without_token_returns_401(self, api_url, unique_email, create_user):
        resp = create_user(unique_email)
        user_id = resp.json()["user"]["user_id"]

        response = requests.get(f"{api_url}/users/{user_id}")

        assert response.status_code == 401

    def test_get_user_with_invalid_token_returns_401(self, api_url, unique_email, create_user):
        resp = create_user(unique_email)
        user_id = resp.json()["user"]["user_id"]

        response = requests.get(
            f"{api_url}/users/{user_id}",
            headers={"Authorization": "Bearer invalid.token.here"},
        )

        assert response.status_code == 401


class TestFullFlow:
    def test_signup_login_and_get_user(self, api_url, admin_headers, unique_email, cleanup):
        """End-to-end: signup -> login -> get user by ID (as admin)."""
        # Signup
        signup_resp = requests.post(
            f"{api_url}/users/signup",
            json={"email": unique_email, "password": "FlowTest1!", "name": "Flow User"},
        )
        assert signup_resp.status_code == 201
        user_id = signup_resp.json()["user"]["user_id"]
        cleanup(user_id)

        # Login
        login_resp = requests.post(
            f"{api_url}/users/login",
            json={"email": unique_email, "password": "FlowTest1!"},
        )
        assert login_resp.status_code == 200
        assert login_resp.json()["user"]["user_id"] == user_id

        # Get user (requires admin)
        get_resp = requests.get(f"{api_url}/users/{user_id}", headers=admin_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["user"]["email"] == unique_email
