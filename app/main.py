from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import router
from app.db import init_db
from app.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown lifecycle."""
    try:
        logger.info("Starting CAIP application...")
        await init_db()
        yield
    except Exception as e:
        logger.exception(f"Startup error: {e}")
    finally:
        logger.info("CAIP application shutting down...")

app = FastAPI(title="Call Analytics & Insights Platform (CAIP)", lifespan=lifespan)
app.include_router(router, prefix="/api")
