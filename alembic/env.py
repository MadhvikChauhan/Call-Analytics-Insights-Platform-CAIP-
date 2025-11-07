
"""Alembic environment for autogeneration using async SQLAlchemy engine.

This env.py is adapted to use the application's settings and asynchronous engine.
Run migrations with the standard Alembic CLI after setting DATABASE_URL.
"""
from logging.config import fileConfig
import os
from sqlalchemy import pool, engine_from_config
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from alembic import context
import asyncio
from app.config import settings
from app.db import Base
from app.logger import get_logger

logger = get_logger(__name__)

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config
# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# set sqlalchemy.url to the app DATABASE_URL for autogenerate
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL.replace('+aiosqlite',''))

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode using async engine."""
    connectable = create_engine(config.get_main_option('sqlalchemy.url'))

    with connectable.connect() as connection:
        do_run_migrations(connection)

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
