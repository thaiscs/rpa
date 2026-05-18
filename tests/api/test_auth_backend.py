from unittest.mock import patch

from fastapi_users.authentication import BearerTransport, JWTStrategy

from api.auth.backend import (
    SESSION_LIFETIME_SECONDS,
    auth_backend,
    bearer_transport,
    get_jwt_strategy,
)


class TestBearerTransport:
    """Tests for bearer transport configuration."""

    def test_bearer_transport_is_correct_type(self):
        """Test that bearer transport is a BearerTransport."""
        assert isinstance(bearer_transport, BearerTransport)


class TestJwtStrategy:
    """Tests for JWT strategy configuration."""

    def test_session_lifetime(self):
        """Test that session lifetime is 8 hours."""
        assert SESSION_LIFETIME_SECONDS == 8 * 60 * 60

    @patch("api.auth.backend.SECRET", "test_secret")
    def test_get_jwt_strategy_returns_jwt_strategy(self):
        """Test that get_jwt_strategy returns a JWTStrategy."""
        strategy = get_jwt_strategy()
        assert isinstance(strategy, JWTStrategy)

    def test_jwt_strategy_uses_correct_secret(self):
        """Test that JWT strategy uses the correct secret."""
        with patch("api.auth.backend.SECRET", "test_secret"):
            strategy = get_jwt_strategy()
            assert strategy.secret == "test_secret"

    @patch("api.auth.backend.SECRET", "test_secret")
    def test_jwt_strategy_uses_correct_lifetime(self):
        """Test that JWT strategy uses correct lifetime."""
        with patch("api.auth.backend.SECRET", "test_secret"):
            strategy = get_jwt_strategy()
            assert strategy.lifetime_seconds == SESSION_LIFETIME_SECONDS


class TestAuthBackend:
    """Tests for authentication backend configuration."""

    def test_auth_backend_name(self):
        """Test that auth backend has correct name."""
        assert auth_backend.name == "jwt"

    def test_auth_backend_transport(self):
        """Test that auth backend uses bearer transport."""
        assert auth_backend.transport == bearer_transport

    @patch("api.auth.backend.SECRET", "test_secret")
    def test_auth_backend_get_strategy(self):
        """Test that auth backend's get_strategy returns JWT strategy."""
        with patch("api.auth.backend.SECRET", "test_secret"):
            strategy = auth_backend.get_strategy()
            assert isinstance(strategy, JWTStrategy)
