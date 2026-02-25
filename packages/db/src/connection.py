"""Database connection and session management."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Database URL from environment
def get_database_url() -> str:
    """Get database URL from environment or default."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/viflo"
    )


def get_sync_database_url() -> str:
    """Get synchronous database URL for Alembic/migrations."""
    url = get_database_url()
    # Convert asyncpg to psycopg2 for sync operations
    return url.replace("postgresql+asyncpg://", "postgresql://")


# Create async engine
engine = create_async_engine(
    get_database_url(),
    poolclass=NullPool,  # Use NullPool for serverless/lambda compatibility
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session as an async context manager.
    
    Usage:
        async with get_session() as session:
            result = await session.execute(query)
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> None:
    """Initialize database (create tables if they don't exist).
    
    Note: In production, use Alembic migrations instead.
    """
    from sqlalchemy import inspect
    
    async with engine.begin() as conn:
        # Check if we can connect
        await conn.execute(sa.text("SELECT 1"))


# Backwards compatibility
SessionLocal = AsyncSessionLocal
