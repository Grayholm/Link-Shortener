from random import choice

from src.exceptions import LinkNotFoundError
from src.models import Links
from src.repository import LinksRepository

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
        await LinksRepository(self.session).add_link(slug, long_url)
        return slug

    async def get_long_url(self, slug: str):
        link = await LinksRepository(self.session).get_link(slug)   
        return link


    async def redirect_to_url(self, slug: str):
        long_url = await self.get_long_url(slug)

        if long_url is None:
            raise LinkNotFoundError(slug)

        return RedirectResponse(url=long_url)
