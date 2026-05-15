import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from shared.db import get_db, DATABASE_URL, engine, AsyncSessionLocal, Base


class TestDatabaseConnection:
    """Tests for database connection utilities."""

    def test_database_url_format(self):
        """Test that DATABASE_URL is correctly formatted."""
        assert DATABASE_URL.startswith("postgresql+asyncpg://")
        assert "certsdb" in DATABASE_URL

    def test_engine_is_created(self):
        """Test that engine is created successfully."""
        assert engine is not None
        assert hasattr(engine, 'connect')

    def test_sessionmaker_is_created(self):
        """Test that AsyncSessionLocal is created."""
        assert AsyncSessionLocal is not None
        assert hasattr(AsyncSessionLocal, '__call__')

    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """Test that get_db yields a valid AsyncSession."""
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            break  # Only test first yield


class TestBase:
    """Tests for SQLAlchemy Base."""

    def test_base_is_declarative(self):
        """Test that Base is a declarative base."""
        assert hasattr(Base, 'metadata')
        assert hasattr(Base, 'registry')
