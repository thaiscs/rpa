import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from api.auth.manager import UserManager, get_user_manager
from shared.models.user import User


class TestUserManager:
    """Tests for UserManager class."""

    def test_user_manager_has_secrets(self):
        """Test that UserManager has correct secrets configured."""
        with patch("api.auth.manager.SECRET", "test_secret"):
            manager = UserManager(None)
            assert manager.reset_password_token_secret == "test_secret"
            assert manager.verification_token_secret == "test_secret"


class TestGetUserManager:
    """Tests for get_user_manager dependency."""

    @pytest.mark.asyncio
    @patch("api.auth.manager.SECRET", "test_secret")
    async def test_get_user_manager_yields_user_manager(self, mock_db_session):
        """Test that get_user_manager yields a UserManager."""
        with patch("api.auth.manager.SQLAlchemyUserDatabase") as mock_db_class:
            mock_db_class.return_value = MagicMock()

            async for manager in get_user_manager(mock_db_session):
                assert isinstance(manager, UserManager)
                break

    @pytest.mark.asyncio
    @patch("api.auth.manager.SECRET", "test_secret")
    async def test_get_user_manager_uses_correct_database(self, mock_db_session):
        """Test that get_user_manager uses the correct database."""
        with patch("api.auth.manager.SQLAlchemyUserDatabase") as mock_db_class:
            mock_db_instance = MagicMock()
            mock_db_class.return_value = mock_db_instance

            async for manager in get_user_manager(mock_db_session):
                mock_db_class.assert_called_once_with(mock_db_session, User)
                break
