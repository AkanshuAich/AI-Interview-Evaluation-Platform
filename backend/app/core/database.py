"""
Database configuration with async SQLAlchemy and connection pooling.
Provides database session management and base model class.
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Fix DATABASE_URL for async driver
# Render provides postgresql:// but we need postgresql+asyncpg://
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Create async engine with connection pooling
# pool_size: number of connections to maintain
# max_overflow: additional connections that can be created when pool is exhausted
# pool_pre_ping: verify connections before using them
engine = create_async_engine(
    database_url,
    echo=False,  # Set to True for SQL query logging in development
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for all database models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    Dependency function that provides database sessions to route handlers.
    Ensures proper session cleanup after request completion.
    
    Usage:
        @router.get("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            # Use db session here
            pass
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database by creating all tables.
    This is called on application startup.
    In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")


async def close_db():
    """
    Close database connections on application shutdown.
    """
    await engine.dispose()
    logger.info("Database connections closed")
