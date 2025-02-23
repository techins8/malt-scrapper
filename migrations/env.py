import os
import sys

base_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(base_dir)

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.core.config import config
from app.core.database import Base
from app.models.malt_profile import MaltProfile  # Import all models here

context_config = context.config

if context_config.config_file_name is not None:
    fileConfig(context_config.config_file_name)

target_metadata = Base.metadata

def get_url():
    return config.DATABASE_URL

def run_migrations_offline() -> None:
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
    configuration = context_config.get_section(context_config.config_ini_section)
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
