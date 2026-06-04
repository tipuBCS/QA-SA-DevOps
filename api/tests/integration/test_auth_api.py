import pytest
import requests

pytestmark = pytest.mark.integration


class TestLoginReturnsToken:
    def test_login_returns_jwt_token(self, api_url, create_user, unique_email):
        """After login, the response should include a JWT token."""
        create_user(email=unique_email)

        response = requests.post(
            f"{api_url}/users/login",
            json={"email": unique_email, "password": "TestPass123"},
        )
        assert response.status_code == 200

        data = response.json()
        assert "token" in data, "Login response should include a token"
        assert isinstance(data["token"], str)
        assert len(data["token"]) > 0

    def test_login_token_contains_user_info(self, api_url, create_user, unique_email):
        """The token payload should contain user identity claims."""
        create_user(email=unique_email)

        response = requests.post(
            f"{api_url}/users/login",
            json={"email": unique_email, "password": "TestPass123"},
        )
        data = response.json()

        assert "user" in data
        assert data["user"]["email"] == unique_email

    def test_invalid_login_does_not_return_token(self, api_url, create_user, unique_email):
        """Failed login should not return a token."""
        create_user(email=unique_email)

        response = requests.post(
            f"{api_url}/users/login",
            json={"email": unique_email, "password": "WrongPassword1"},
        )
        assert response.status_code == 401

        data = response.json()
        assert "token" not in data


class TestProtectedEndpoints:
    def test_get_user_with_valid_token(self, api_url, admin_headers, create_user, unique_email):
        """Protected endpoints should accept a valid admin JWT token."""
        signup_response = create_user(email=unique_email)
        user_id = signup_response.json()["user"]["user_id"]

        # Access protected endpoint with admin token
        response = requests.get(
            f"{api_url}/users/{user_id}",
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["user"]["email"] == unique_email

    def test_get_user_without_token_returns_401(self, api_url, create_user, unique_email):
        """Protected endpoints should reject requests without a token."""
        signup_response = create_user(email=unique_email)
        user_id = signup_response.json()["user"]["user_id"]

        response = requests.get(f"{api_url}/users/{user_id}")
        assert response.status_code == 401

    def test_get_user_with_invalid_token_returns_401(self, api_url, create_user, unique_email):
        """Protected endpoints should reject invalid tokens."""
        signup_response = create_user(email=unique_email)
        user_id = signup_response.json()["user"]["user_id"]

        response = requests.get(
            f"{api_url}/users/{user_id}",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401
