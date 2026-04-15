from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:6432/short_links"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)