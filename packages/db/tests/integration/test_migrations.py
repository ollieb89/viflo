"""Integration tests for database migrations."""

import asyncio
import os
import uuid
from datetime import datetime

import pytest
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Ensure we use test database
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/viflo")

from connection import get_database_url, get_session
from models import Project


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create a database engine for testing."""
    database_url = get_database_url()
    engine = create_async_engine(
        database_url,
        poolclass=NullPool,
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def session(engine):
    """Create a database session for each test."""
    async with engine.begin() as conn:
        # Clean up any test data
        await conn.execute(sa.text("TRUNCATE TABLE projects RESTART IDENTITY CASCADE"))
    
    async with get_session() as session:
        yield session


class TestMigrations:
    """Test that migrations work correctly."""

    @pytest.mark.asyncio
    async def test_can_connect_to_database(self, engine):
        """Test that we can connect to the database."""
        async with engine.connect() as conn:
            result = await conn.execute(sa.text("SELECT 1"))
            assert result.scalar() == 1

    @pytest.mark.asyncio
    async def test_projects_table_exists(self, engine):
        """Test that the projects table was created by migration."""
        async with engine.connect() as conn:
            # Check if table exists
            result = await conn.execute(
                sa.text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'projects'
                    )
                """)
            )
            assert result.scalar() is True

    @pytest.mark.asyncio
    async def test_can_create_and_retrieve_project(self, session):
        """Test CRUD operations on Project model."""
        # Create a project
        project_id = uuid.uuid4()
        project_name = "Test Project"
        
        await session.execute(
            sa.text("""
                INSERT INTO projects (id, name, description, created_at)
                VALUES (:id, :name, :description, NOW())
            """),
            {
                "id": str(project_id),
                "name": project_name,
                "description": "A test project for integration testing",
            }
        )
        await session.commit()
        
        # Retrieve the project
        result = await session.execute(
            sa.text("SELECT id, name, description FROM projects WHERE id = :id"),
            {"id": str(project_id)}
        )
        row = result.fetchone()
        
        assert row is not None
        assert str(row.id) == str(project_id)
        assert row.name == project_name
        assert row.description == "A test project for integration testing"

    @pytest.mark.asyncio
    async def test_project_has_required_columns(self, engine):
        """Test that projects table has expected columns."""
        async with engine.connect() as conn:
            result = await conn.execute(
                sa.text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'projects'
                    ORDER BY ordinal_position
                """)
            )
            columns = {row.column_name: row for row in result.fetchall()}
            
            # Check required columns exist
            assert "id" in columns
            assert "name" in columns
            assert "description" in columns
            assert "created_at" in columns
            assert "updated_at" in columns
            
            # Check id is not nullable (primary key)
            assert columns["id"].is_nullable == "NO"
            
            # Check name is not nullable
            assert columns["name"].is_nullable == "NO"


class TestConnection:
    """Test database connection utilities."""

    def test_get_database_url_from_environment(self, monkeypatch):
        """Test that DATABASE_URL is read from environment."""
        test_url = "postgresql+asyncpg://test:test@localhost:5432/testdb"
        monkeypatch.setenv("DATABASE_URL", test_url)
        
        from connection import get_database_url
        assert get_database_url() == test_url

    def test_get_database_url_default(self, monkeypatch):
        """Test that default URL is used when env var not set."""
        monkeypatch.delenv("DATABASE_URL", raising=False)
        
        from connection import get_database_url
        url = get_database_url()
        assert "localhost:5432" in url
        assert "viflo" in url
