
import asyncio

from alembic import context

from app.db.database import engine
from app.db.models import Base, GeneratedContent  # noqa: F401

# Alembic configuration
config = context.config

# Load SQLAlchemy model metadata
target_metadata = Base.metadata


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    raise RuntimeError(
        "Offline migrations are not configured. "
        "Run Alembic with database connectivity."
    )
else:
    run_migrations_online()
