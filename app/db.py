
"""Database utilities with logging and error handling."""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
from .logger import get_logger

logger = get_logger(__name__)

# Async engine & session factory
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Declarative base for ORM models
Base = declarative_base()

async def init_db():
    """Create database tables and log progress.

    This function is safe to call at app startup; exceptions are logged.
    """
    try:
        logger.info("Initializing database and creating tables if not present.")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialization complete.")
    except Exception as exc:
        logger.exception("Failed to initialize database: %s", exc)
        raise
