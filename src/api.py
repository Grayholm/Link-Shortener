from fastapi import APIRouter, Depends, HTTPException, status

from src.dependencies import get_db
from src.exceptions import LinkNotFoundError
from src.service import LinkShortenerService

router = APIRouter(
    prefix="/api",
    tags=["api"],
)


@router.post("/short-links")
async def create_short_link_API(long_url: str, session=Depends(get_db)):
    res = await LinkShortenerService(session).create_short_link(long_url)
    return {"short_link": res}
    

@router.get("/short-links/{slug}")
async def redirect_to_url_API(slug: str, session=Depends(get_db)):
    try:
        return await LinkShortenerService(session).redirect_to_url(slug)
    except LinkNotFoundError as e:
        raise HTTPException(detail=e.detail, status_code=status.HTTP_404_NOT_FOUND)