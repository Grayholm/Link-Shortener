
from fastapi import APIRouter, Depends, HTTPException, status
import logging

from fastapi.responses import RedirectResponse

from src.dependencies import get_db
from src.exceptions import LinkNotFoundError
from src.service import LinkShortenerService

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

        long_url = await LinkShortenerService(session).redirect_to_url(slug)

        return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
    except LinkNotFoundError as e:

        logger.error(f"Link not found for slug: {slug}")

        raise HTTPException(detail=e.detail, status_code=status.HTTP_404_NOT_FOUND)