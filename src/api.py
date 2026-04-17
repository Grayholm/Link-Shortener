from fastapi import APIRouter, Body, Depends, HTTPException, status
import logging

from fastapi.responses import RedirectResponse

from src.dependencies import get_db
from src.exceptions import LinkNotFoundError
from src.scheme import ShortLinkRequest
from src.service import LinkShortenerService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api",
    tags=["api"],
)


@router.post("/short-links", summary="Create a short link from a long URL")
async def create_short_link_API(
    long_url: ShortLinkRequest = Body(...), session=Depends(get_db)
):

    logger.info(f"API call to create short link for URL: {str(long_url.long_url)}")

    res = await LinkShortenerService(session).create_short_link(str(long_url.long_url))
    return {"slug": res}


@router.get(
    "/short-links/{slug}", summary="Redirect to the original URL using the short link"
)
async def redirect_to_url_API(slug: str, session=Depends(get_db)):
    logger.info(f"API call to redirect for slug: {slug}")
    try:
        long_url = await LinkShortenerService(session).redirect_to_url(slug)
        return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
    except LinkNotFoundError as e:
        logger.warning(f"Link not found for slug: {slug}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.detail))
