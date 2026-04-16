from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from src.models import Links


class LinksRepository:
    def __init__(self, session):
        self.session = session

    async def add_link(self, slug: str, url: str):
        try:
            add_stmt = insert(Links).values(slug=slug, url=url)
            await self.session.execute(add_stmt)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise e
    
    async def get_link(self, slug: str):
        stmt = select(Links.url).where(Links.slug == slug)
        result = await self.session.execute(stmt)
        link = result.scalar_one_or_none()
        return link