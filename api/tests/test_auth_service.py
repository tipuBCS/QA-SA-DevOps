import time

import pytest

from services.auth_service import AuthService

pytestmark = pytest.mark.unit

class TestCreateToken:
    def test_creates_valid_token(self):
        token = AuthService.create_token(
            user_id="user-123",
            email="test@example.com",
            is_admin=False,
            access_level=2,
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_correct_claims(self):
        token = AuthService.create_token(
            user_id="user-456",
            email="admin@example.com",
            is_admin=True,
            access_level=4,
        )
        payload = AuthService.decode_token(token)

        assert payload["sub"] == "user-456"
        assert payload["email"] == "admin@example.com"
        assert payload["is_admin"] is True
        assert payload["access_level"] == 4
        assert "iat" in payload
        assert "exp" in payload

    def test_token_expiry_is_in_future(self):
        token = AuthService.create_token(
            user_id="user-789",
            email="user@example.com",
            is_admin=False,
            access_level=1,
        )
        payload = AuthService.decode_token(token)

        assert payload["exp"] > payload["iat"]


class TestDecodeToken:
    def test_decodes_valid_token(self):
        token = AuthService.create_token(
            user_id="user-123",
            email="test@example.com",
            is_admin=False,
            access_level=1,
        )
        payload = AuthService.decode_token(token)

        assert payload["sub"] == "user-123"
        assert payload["email"] == "test@example.com"

    def test_raises_for_invalid_token(self):
        with pytest.raises(ValueError, match="Invalid token"):
            AuthService.decode_token("not.a.valid.token")

    def test_raises_for_tampered_token(self):
        token = AuthService.create_token(
            user_id="user-123",
            email="test@example.com",
            is_admin=False,
            access_level=1,
        )
        # Tamper with the token by changing a character
        tampered = token[:-5] + "XXXXX"

        with pytest.raises(ValueError, match="Invalid token"):
            AuthService.decode_token(tampered)

    def test_raises_for_expired_token(self, monkeypatch):
        # Set expiry to 0 hours so token is immediately expired
        monkeypatch.setattr("services.auth_service.JWT_EXPIRY_HOURS", 0)

        token = AuthService.create_token(
            user_id="user-123",
            email="test@example.com",
            is_admin=False,
            access_level=1,
        )

        # Token with 0 hour expiry means exp == iat, so it's already expired
        time.sleep(1)

        with pytest.raises(ValueError, match="Token has expired"):
            AuthService.decode_token(token)


class TestGetUserFromToken:
    def test_returns_user_dict(self):
        token = AuthService.create_token(
            user_id="user-abc",
            email="hello@example.com",
            is_admin=True,
            access_level=3,
        )
        user = AuthService.get_user_from_token(token)

        assert user == {
            "user_id": "user-abc",
            "email": "hello@example.com",
            "is_admin": True,
            "access_level": 3,
        }

    def test_raises_for_invalid_token(self):
        with pytest.raises(ValueError):
            AuthService.get_user_from_token("garbage")


class TestExtractTokenFromHeader:
    def test_extracts_token_from_valid_header(self):
        token = AuthService.extract_token_from_header("Bearer my-jwt-token")
        assert token == "my-jwt-token"

    def test_case_insensitive_bearer(self):
        token = AuthService.extract_token_from_header("bearer my-jwt-token")
        assert token == "my-jwt-token"

    def test_raises_for_missing_header(self):
        with pytest.raises(ValueError, match="Missing Authorization header"):
            AuthService.extract_token_from_header(None)

    def test_raises_for_empty_header(self):
        with pytest.raises(ValueError, match="Missing Authorization header"):
            AuthService.extract_token_from_header("")

    def test_raises_for_missing_bearer_prefix(self):
        with pytest.raises(ValueError, match="Invalid Authorization header format"):
            AuthService.extract_token_from_header("Token my-jwt-token")

    def test_raises_for_malformed_header(self):
        with pytest.raises(ValueError, match="Invalid Authorization header format"):
            AuthService.extract_token_from_header("Bearer")
