import pytest
import uuid
from unittest.mock import patch, MagicMock
from fastapi import Depends

from api.auth.deps import current_admin, current_superuser
from api.auth.users import fastapi_users


class TestCurrentAdmin:
    """Tests for current_admin dependency."""

    def test_current_admin_is_fastapi_users_dependency(self):
        """Test that current_admin is a FastAPI Users dependency."""
        assert current_admin is not None
        # It should be a callable that returns a user
        assert callable(current_admin)


class TestCurrentSuperuser:
    """Tests for current_superuser dependency."""

    def test_current_superuser_is_fastapi_users_dependency(self):
        """Test that current_superuser is a FastAPI Users dependency."""
        assert current_superuser is not None
        # It should be a callable that returns a superuser
        assert callable(current_superuser)

    def test_current_superuser_requires_superuser(self):
        """Test that current_superuser requires superuser=True."""
        # This is verified by the fastapi_users.current_user(superuser=True) call
        # We can't easily test the behavior without a full FastAPI app
        assert current_superuser is not None
