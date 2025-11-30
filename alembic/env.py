import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. Add the project root to the system path so we can import 'app'
sys.path.insert(0, os.path.abspath("."))

# 2. Import your SQLModel and the config settings
from sqlmodel import SQLModel
from app.core.config import settings
from app.models import *  # This imports all your tables (User, Book, etc.)

# 3. This tells Alembic about your models
target_metadata = SQLModel.metadata

# Config setup
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_url():
    """Load the DB URL from .env settings"""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generating SQL script)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connecting to DB)."""

    # Create configuration with the URL from .env
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()