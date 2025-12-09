# Alembic environment configuration
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.db import Base

# Import all models to ensure they're registered with SQLAlchemy
from app.domain.entities.models import Entity, Person, Address
from app.domain.properties.models import Property
from app.domain.graph.models import Relationship, Event, RiskScore

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add model metadata for 'autogenerate' support
target_metadata = Base.metadata

# Override SQLAlchemy URL with our settings
config.set_main_option('sqlalchemy.url', str(settings.database_url))


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Include object names for better autogenerate
            include_object=include_object,
            # Render item for custom types
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter objects to include in migrations.
    """
    # Skip tables that aren't part of our models
    if type_ == "table" and name in ["alembic_version"]:
        return False
    
    return True


def render_item(type_, obj, autogen_context):
    """
    Apply custom rendering for certain types.
    """
    # Import custom types here if needed
    return False


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()