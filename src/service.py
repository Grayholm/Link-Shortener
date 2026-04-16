import logging
from random import choice

from src.exceptions import LinkNotFoundError
from src.repository import LinksRepository

from fastapi.responses import RedirectResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Creating short link for URL: {long_url}")
        slug = self.generate_short_link()
        await LinksRepository(self.session).add_link(slug, long_url)
        return slug

    async def get_long_url(self, slug: str):
        logger.info(f"Getting long URL for slug: {slug}")
        link = await LinksRepository(self.session).get_link(slug)   
        return link


    async def redirect_to_url(self, slug: str):
        logger.info(f"Redirecting to URL for slug: {slug}")
        long_url = await self.get_long_url(slug)

        if long_url is None:
            logger.error(f"Link not found for slug: {slug}")
            raise LinkNotFoundError(slug)

        return long_url
