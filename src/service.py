import logging
from random import choice

from sqlalchemy.exc import IntegrityError
from pydantic import HttpUrl

from src.exceptions import IsNotDoneToCreateUniqueLinkError, LinkNotFoundError
from src.repository import LinksRepository
from src.database.redis_config import redis_manager

logger = logging.getLogger(__name__)

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
SLUG_LENGTH = 6
MAX_CREATE_RETRIES = 5

class LinkShortenerService:
    def __init__(self, session):
        self.session = session
        self.redis = redis_manager

    async def generate_short_link(self):
        return "".join(choice(ALPHABET) for _ in range(SLUG_LENGTH))


    async def create_short_link(self, long_url: HttpUrl):
        logger.info(f"Creating short link for URL: {long_url}")
        repository = LinksRepository(self.session)

        for attempt in range(MAX_CREATE_RETRIES):
            slug = await self.generate_short_link()
            try:
                await repository.add_link(slug, long_url)
                return slug
            except IntegrityError:
                logger.warning(
                    "Slug collision for %s on attempt %s",
                    slug,
                    attempt + 1,
                )

        logger.error("Failed to create unique slug after %s attempts", MAX_CREATE_RETRIES)
        raise IsNotDoneToCreateUniqueLinkError()

    async def get_long_url(self, slug: str):
        logger.info(f"Getting long URL for slug: {slug}")
        link = await LinksRepository(self.session).get_link(slug)   
        return link


    async def redirect_to_url(self, slug: str):
        logger.info(f"Redirecting to URL for slug: {slug}")

        key = f"redirect:{slug}"
        try:
            value = await self.redis.get_value(key)
            if value is not None:
                logger.info(f"Cache hit for slug: {slug}")
                return value
        except Exception as e:
            logger.warning("Redis read failed for slug %s: %s", slug, e)
        
        long_url = await self.get_long_url(slug)

        if long_url is None:
            logger.error(f"Link not found for slug: {slug}")
            raise LinkNotFoundError(slug)

        try:
            await self.redis.set_value(key, long_url, ttl=300)
        except Exception as e:
            logger.warning("Redis write failed for slug %s: %s", slug, e)

        return long_url
