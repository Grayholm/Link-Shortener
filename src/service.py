from random import choice

from src.exceptions import LinkNotFoundError
from src.models import Links

from sqlalchemy import insert, select
from fastapi.responses import RedirectResponse


ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

class LinkShortenerService:
    def __init__(self, session):
        self.session = session

    def generate_short_link(self):
        slug = ""
        for _ in range(6):
            slug += choice(ALPHABET)
        return slug


    async def create_short_link(self, long_url: str):
        slug = self.generate_short_link()
        add_stmt = insert(Links).values(slug=slug, url=long_url)
        await self.session.execute(add_stmt)
        await self.session.commit()
        return slug

    async def get_long_url(self, slug: str):
        stmt = select(Links.url).where(Links.slug == slug)

        result = await self.session.execute(stmt)
        link = result.scalar_one_or_none()
        print(link)
        return link


    async def redirect_to_url(self, slug: str):
        long_url = await self.get_long_url(slug)

        if long_url is None:
            raise LinkNotFoundError(slug)

        return RedirectResponse(url=long_url)
