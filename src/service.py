import logging
from random import choice

from src.exceptions import LinkAlreadyExistsError, LinkNotFoundError
from src.repository import LinksRepository
from src.redis_config import redis_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

class LinkShortenerService:
    def __init__(self, session):
        self.session = session
        self.redis = redis_manager

    async def generate_short_link(self):
        slug = ""
        for _ in range(6):
            slug += choice(ALPHABET)
        
        if await LinksRepository(self.session).get_link(slug) is not None:
            return await self.generate_short_link()
        else:
            return slug


    async def create_short_link(self, long_url: str):
        logger.info(f"Creating short link for URL: {long_url}")
        slug = await self.generate_short_link()
        await LinksRepository(self.session).add_link(slug, long_url)
        return slug

    async def get_long_url(self, slug: str):
        logger.info(f"Getting long URL for slug: {slug}")
        link = await LinksRepository(self.session).get_link(slug)   
        return link


    async def redirect_to_url(self, slug: str):
        logger.info(f"Redirecting to URL for slug: {slug}")

        key = f"redirect:{slug}"
        value = await self.redis.get_value(key)
        if value is not None:
            logger.info(f"Cache hit for slug: {slug}")
            return value
        
        long_url = await self.get_long_url(slug)

        if long_url is None:
            logger.error(f"Link not found for slug: {slug}")
            raise LinkNotFoundError(slug)

        await self.redis.set_value(key, long_url, ttl=300)

        return long_url
