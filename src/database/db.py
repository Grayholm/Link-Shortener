from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.database.config import settings

engine = create_async_engine(settings.db_url, echo=True)
async_session: async_sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)