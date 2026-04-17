from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.database.config import settings

engine = create_async_engine(settings.db_url, echo=True)
engine_null_pool = create_async_engine(settings.db_url, echo=True, poolclass=NullPool)

async_session: async_sessionmaker = async_sessionmaker(
    bind=engine, expire_on_commit=False
)
async_session_null_pool: async_sessionmaker = async_sessionmaker(
    bind=engine_null_pool, expire_on_commit=False
)
