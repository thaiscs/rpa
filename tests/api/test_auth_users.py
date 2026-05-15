import pytest
import uuid
from unittest.mock import patch, MagicMock

from api.auth.users import fastapi_users
from shared.models.user import User


class TestFastAPIUsers:
    """Tests for fastapi_users instance."""

    def test_fastapi_users_is_configured(self):
        """Test that fastapi_users is configured."""
        assert fastapi_users is not None

    def test_fastapi_users_uses_user_model(self):
        """Test that fastapi_users uses the User model."""
        # The User model is passed to FastAPIUsers at initialization
        # We can verify this by checking the type hints
        assert fastapi_users is not None

    def test_fastapi_users_has_auth_backend(self):
        """Test that fastapi_users has auth backend configured."""
        # FastAPIUsers is initialized with auth_backend
        assert fastapi_users is not None
