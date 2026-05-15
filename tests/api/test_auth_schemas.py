import pytest
import uuid
from pydantic import ValidationError

from api.auth.schemas import UserRead, UserCreate, UserUpdate


class TestUserRead:
    """Tests for UserRead schema."""

    def test_user_read_with_valid_data(self):
        """Test UserRead with valid data."""
        user_id = uuid.uuid4()
        data = {
            "id": user_id,
            "email": "test@example.com",
            "is_active": True,
            "is_superuser": False,
            "is_verified": True,
            "name": "Test User",
            "client_id": None
        }
        user = UserRead(**data)
        assert user.id == user_id
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.client_id is None

    def test_user_read_with_client_id(self):
        """Test UserRead with client_id."""
        user_id = uuid.uuid4()
        client_id = uuid.uuid4()
        data = {
            "id": user_id,
            "email": "test@example.com",
            "is_active": True,
            "is_superuser": False,
            "is_verified": True,
            "name": "Test User",
            "client_id": client_id
        }
        user = UserRead(**data)
        assert user.client_id == client_id

    def test_user_read_optional_name(self):
        """Test that name is optional."""
        user_id = uuid.uuid4()
        data = {
            "id": user_id,
            "email": "test@example.com",
            "is_active": True,
            "is_superuser": False,
            "is_verified": True
        }
        user = UserRead(**data)
        assert user.name is None


class TestUserCreate:
    """Tests for UserCreate schema."""

    def test_user_create_with_valid_data(self):
        """Test UserCreate with valid data."""
        data = {
            "email": "newuser@example.com",
            "password": "securepassword123",
            "name": "New User"
        }
        user = UserCreate(**data)
        assert user.email == "newuser@example.com"
        assert user.password == "securepassword123"
        assert user.name == "New User"

    def test_user_create_without_name(self):
        """Test UserCreate without name."""
        data = {
            "email": "newuser@example.com",
            "password": "securepassword123"
        }
        user = UserCreate(**data)
        assert user.name is None

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email."""
        data = {
            "email": "invalid-email",
            "password": "securepassword123"
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)


class TestUserUpdate:
    """Tests for UserUpdate schema."""

    def test_user_update_with_name(self):
        """Test UserUpdate with name."""
        data = {
            "name": "Updated Name"
        }
        user = UserUpdate(**data)
        assert user.name == "Updated Name"

    def test_user_update_with_password(self):
        """Test UserUpdate with password."""
        data = {
            "password": "newpassword123"
        }
        user = UserUpdate(**data)
        assert user.password == "newpassword123"

    def test_user_update_empty(self):
        """Test UserUpdate with no fields."""
        user = UserUpdate()
        assert user.name is None
        assert user.password is None
