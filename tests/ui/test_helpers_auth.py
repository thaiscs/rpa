import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ui.helpers.auth import Auth, protected


@pytest.fixture
def mock_app_storage():
    """Create a mock NiceGUI app.storage."""
    storage = MagicMock()
    storage.user = {}
    return storage


@pytest.fixture
def mock_httpx_client():
    """Create a mock httpx.AsyncClient."""
    client = AsyncMock()
    return client


class TestAuthToken:
    """Tests for Auth.token method."""

    def test_token_returns_valid_token(self, mock_app_storage):
        """Test that token returns valid token."""
        mock_app_storage.user["token"] = "valid_token"
        mock_app_storage.user["expires_at"] = time.time() + 3600

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth.token()
            assert result == "valid_token"

    def test_token_returns_none_if_expired(self, mock_app_storage):
        """Test that token returns None if expired."""
        mock_app_storage.user["token"] = "expired_token"
        mock_app_storage.user["expires_at"] = time.time() - 3600

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth.token()
            assert result is None

    def test_token_returns_none_if_no_token(self, mock_app_storage):
        """Test that token returns None if no token exists."""
        mock_app_storage.user = {}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth.token()
            assert result is None


class TestAuthIsExpired:
    """Tests for Auth._is_expired method."""

    def test_is_expired_true(self, mock_app_storage):
        """Test that _is_expired returns True for expired token."""
        mock_app_storage.user["expires_at"] = time.time() - 3600

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth._is_expired()
            assert result is True

    def test_is_expired_false(self, mock_app_storage):
        """Test that _is_expired returns False for valid token."""
        mock_app_storage.user["expires_at"] = time.time() + 3600

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth._is_expired()
            assert result is False

    def test_is_expired_no_expiration(self, mock_app_storage):
        """Test that _is_expired returns False if no expiration."""
        mock_app_storage.user = {}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth._is_expired()
            assert result is False


class TestAuthFetchUser:
    """Tests for Auth.fetch_user method."""

    @pytest.mark.asyncio
    async def test_fetch_user_success(self, mock_app_storage):
        """Test successful user fetch."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"id": "123", "email": "test@example.com"}

        inner_client = AsyncMock()
        inner_client.get.return_value = response

        mock_client_cls = MagicMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=inner_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("ui.helpers.auth.httpx.AsyncClient", mock_client_cls), \
             patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):

            await Auth.fetch_user("valid_token")
            assert mock_app_storage.user["user"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_fetch_user_failure(self, mock_app_storage):
        """Test user fetch on API failure."""
        inner_client = AsyncMock()
        inner_client.get.side_effect = Exception("API error")

        mock_client_cls = MagicMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=inner_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("ui.helpers.auth.httpx.AsyncClient", mock_client_cls), \
             patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):

            await Auth.fetch_user("valid_token")
            # Should not crash, just log error
            assert "user" not in mock_app_storage.user


class TestAuthLogin:
    """Tests for Auth.login method."""

    @pytest.mark.asyncio
    async def test_login_stores_token(self, mock_app_storage):
        """Test that login stores token and expiration."""
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = {"id": "123", "email": "test@example.com"}

        inner_client = AsyncMock()
        inner_client.get.return_value = response

        mock_client_cls = MagicMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=inner_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("ui.helpers.auth.httpx.AsyncClient", mock_client_cls), \
             patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            await Auth.login("test_token")

            assert mock_app_storage.user["token"] == "test_token"
            assert "expires_at" in mock_app_storage.user
            assert mock_app_storage.user["expires_at"] > time.time()


class TestAuthLogout:
    """Tests for Auth.logout method."""

    def test_logout_clears_data(self, mock_app_storage):
        """Test that logout clears all auth data."""
        mock_app_storage.user["token"] = "test_token"
        mock_app_storage.user["expires_at"] = time.time() + 3600
        mock_app_storage.user["user"] = {"id": "123"}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            Auth.logout()

            assert "token" not in mock_app_storage.user
            assert "expires_at" not in mock_app_storage.user
            assert "user" not in mock_app_storage.user


class TestAuthIsLoggedIn:
    """Tests for Auth.is_logged_in method."""

    def test_is_logged_in_true(self, mock_app_storage):
        """Test that is_logged_in returns True when logged in."""
        mock_app_storage.user["token"] = "valid_token"

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth.is_logged_in()
            assert result is True

    def test_is_logged_in_false(self, mock_app_storage):
        """Test that is_logged_in returns False when not logged in."""
        mock_app_storage.user = {}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth.is_logged_in()
            assert result is False


class TestAuthIsSuperuser:
    """Tests for Auth.is_superuser method."""

    def test_is_superuser_true(self, mock_app_storage):
        """Test that is_superuser returns True for superuser."""
        mock_app_storage.user["user"] = {"is_superuser": True}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth.is_superuser()
            assert result is True

    def test_is_superuser_false(self, mock_app_storage):
        """Test that is_superuser returns False for regular user."""
        mock_app_storage.user["user"] = {"is_superuser": False}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth.is_superuser()
            assert result is False

    def test_is_superuser_no_user(self, mock_app_storage):
        """Test that is_superuser returns False when no user."""
        mock_app_storage.user = {}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth.is_superuser()
            assert result is False


class TestAuthUser:
    """Tests for Auth.user method."""

    def test_user_returns_user_data(self, mock_app_storage):
        """Test that user returns user data."""
        mock_app_storage.user["user"] = {"id": "123", "email": "test@example.com"}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth.user()
            assert result["email"] == "test@example.com"

    def test_user_returns_none(self, mock_app_storage):
        """Test that user returns None when no user."""
        mock_app_storage.user = {}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)):
            result = Auth.user()
            assert result is None


class TestProtectedDecorator:
    """Tests for protected decorator."""

    def test_protected_creates_decorator(self):
        """Test that protected creates a decorator."""
        decorator = protected("/test")
        assert callable(decorator)

    def test_protected_with_superuser(self):
        """Test that protected with superuser flag."""
        decorator = protected("/test", superuser=True)
        assert callable(decorator)


class TestProtectedDecoratorBehavior:
    """Tests verifying the wrapper logic inside the protected decorator."""

    def _make_mock_ui(self):
        """Return a mock ui where ui.page(route) is a pass-through decorator."""
        mock_ui = MagicMock()
        mock_ui.page.return_value = lambda func: func
        return mock_ui

    async def test_redirects_to_login_when_no_token(self, mock_app_storage):
        mock_ui = self._make_mock_ui()
        mock_app_storage.user = {}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)), \
             patch("ui.helpers.auth.ui", mock_ui):

            @protected("/guarded")
            async def guarded_page():
                pass  # pragma: no cover

            await guarded_page()

        mock_ui.navigate.to.assert_called_once_with("/login")
        notify_msg = mock_ui.notify.call_args[0][0]
        assert "necessário" in notify_msg

    async def test_shows_session_expired_message_for_expired_token(self, mock_app_storage):
        import time
        mock_ui = self._make_mock_ui()
        mock_app_storage.user = {
            "token": "old_token",
            "expires_at": time.time() - 3600,
        }

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)), \
             patch("ui.helpers.auth.ui", mock_ui):

            @protected("/guarded")
            async def guarded_page():
                pass  # pragma: no cover

            await guarded_page()

        mock_ui.navigate.to.assert_called_once_with("/login")
        notify_msg = mock_ui.notify.call_args[0][0]
        assert "expirada" in notify_msg.lower()

    async def test_calls_page_function_when_logged_in(self, mock_app_storage):
        import time
        mock_ui = self._make_mock_ui()
        mock_app_storage.user = {
            "token": "valid_token",
            "expires_at": time.time() + 3600,
            "user": {"email": "u@test.com", "is_superuser": False},
        }
        called = {"n": 0}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)), \
             patch("ui.helpers.auth.ui", mock_ui):

            @protected("/guarded")
            def guarded_page():
                called["n"] += 1

            await guarded_page()

        assert called["n"] == 1
        mock_ui.navigate.to.assert_not_called()

    async def test_blocks_non_superuser_from_superuser_page(self, mock_app_storage):
        import time
        mock_ui = self._make_mock_ui()
        mock_app_storage.user = {
            "token": "valid_token",
            "expires_at": time.time() + 3600,
            "user": {"email": "u@test.com", "is_superuser": False},
        }
        called = {"n": 0}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)), \
             patch("ui.helpers.auth.ui", mock_ui):

            @protected("/admin-only", superuser=True)
            def admin_page():
                called["n"] += 1  # pragma: no cover

            await admin_page()

        assert called["n"] == 0
        notify_msg = mock_ui.notify.call_args[0][0]
        assert "administradores" in notify_msg

    async def test_allows_superuser_to_access_superuser_page(self, mock_app_storage):
        import time
        mock_ui = self._make_mock_ui()
        mock_app_storage.user = {
            "token": "valid_token",
            "expires_at": time.time() + 3600,
            "user": {"email": "admin@test.com", "is_superuser": True},
        }
        called = {"n": 0}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)), \
             patch("ui.helpers.auth.ui", mock_ui):

            @protected("/admin-only", superuser=True)
            def admin_page():
                called["n"] += 1

            await admin_page()

        assert called["n"] == 1

    async def test_awaits_async_page_function(self, mock_app_storage):
        import time
        mock_ui = self._make_mock_ui()
        mock_app_storage.user = {
            "token": "valid_token",
            "expires_at": time.time() + 3600,
            "user": {"email": "u@test.com", "is_superuser": False},
        }
        called = {"n": 0}

        with patch("ui.helpers.auth.app", MagicMock(storage=mock_app_storage)), \
             patch("ui.helpers.auth.ui", mock_ui):

            @protected("/guarded")
            async def guarded_page():
                called["n"] += 1

            await guarded_page()

        assert called["n"] == 1
