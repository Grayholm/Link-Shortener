
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from fastapi.responses import RedirectResponse

from src.dependencies import get_db
from src.exceptions import LinkNotFoundError
from src.service import LinkShortenerService
from src.redis_config import redis_manager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["api"],
)

@router.post("/short-links", summary="Create a short link from a long URL")
async def create_short_link_API(long_url: str, session=Depends(get_db)):

    logger.info(f"API call to create short link for URL: {long_url}")

    res = await LinkShortenerService(session).create_short_link(long_url)
    return {"short_link": res}
    

@router.get("/short-links/{slug}", summary="Redirect to the original URL using the short link")
async def redirect_to_url_API(slug: str, session=Depends(get_db)):
    try:

        logger.info(f"API call to redirect for slug: {slug}")

        key = f"redirect:{slug}"
        value = await redis_manager.get_value(key)

        if value is not None:

            logger.info(f"Cache hit for slug: {slug}")

            return RedirectResponse(url=value, status_code=302)

        long_url = await LinkShortenerService(session).redirect_to_url(slug)

        await redis_manager.set_value(key, long_url, ttl=300)

        return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
    except LinkNotFoundError as e:

        logger.error(f"Link not found for slug: {slug}")

        raise HTTPException(detail=e.detail, status_code=302)