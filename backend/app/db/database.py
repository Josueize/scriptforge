
from collections.abc import AsyncGenerator

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# Parse the existing PostgreSQL URL safely.
db_url = make_url(settings.database_url)
db_url = db_url.set(drivername="postgresql+asyncpg")

# asyncpg expects "ssl", not "sslmode".
query = dict(db_url.query)

if "sslmode" in query:
    query["ssl"] = query.pop("sslmode")

db_url = db_url.set(query=query)

engine = create_async_engine(
    db_url,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
