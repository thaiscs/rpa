import pytest
from fastapi_users import FastAPIUsers

from api.auth.users import fastapi_users
from shared.models.user import User


class TestFastAPIUsers:
    """Tests for fastapi_users instance."""

    def test_fastapi_users_is_correct_type(self):
        """Test that fastapi_users is a FastAPIUsers instance."""
        assert isinstance(fastapi_users, FastAPIUsers)

    def test_fastapi_users_exposes_current_user(self):
        """Test that fastapi_users exposes the current_user dependency factory."""
        assert callable(fastapi_users.current_user)
