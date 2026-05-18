
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db import DATABASE_URL, AsyncSessionLocal, Base, engine, get_db


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
        assert callable(AsyncSessionLocal)

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
