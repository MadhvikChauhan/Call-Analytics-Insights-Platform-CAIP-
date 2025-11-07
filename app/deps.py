
"""Dependency utilities for FastAPI routes.

Provides `get_db` for async DB session and `get_company_by_api_key` which
validates the X-API-KEY header and loads the Company instance.
"""
from fastapi import Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from .db import AsyncSessionLocal
from .models import Company

async def get_db():
    """Yield an async SQLAlchemy session.

    This dependency opens a session for the request and ensures it is closed
    when the request is complete.
    """
    async with AsyncSessionLocal() as session:
        yield session

async def get_company_by_api_key(x_api_key: Optional[str] = Header(None), db: AsyncSession = Depends(get_db)) -> Company:
    """Validate X-API-KEY header and return the matching Company.

    Args:
        x_api_key: API key provided by the caller in `X-API-KEY` header.
        db: AsyncSession dependency.

    Raises:
        HTTPException 401 if header missing or key invalid.

    Returns:
        Company ORM instance corresponding to the API key.
    """
    if not x_api_key:
        raise HTTPException(status_code=401, detail="X-API-KEY header required")
    q = select(Company).where(Company.api_key == x_api_key)
    res = await db.execute(q)
    company = res.scalars().first()
    if not company:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return company
