from fastapi import APIRouter, HTTPException, status

from src.exceptions import LinkNotFoundError
from src.service import create_short_link, redirect_to_url

router = APIRouter(
    prefix="/api",
    tags=["api"],
)


@router.post("/short-links")
async def create_short_link_API(long_url: str):
    return await create_short_link(long_url)
    

@router.get("/short-links/{slug}")
async def redirect_to_url_API(slug: str):
    try:
        return await redirect_to_url(slug)
    except LinkNotFoundError as e:
        raise HTTPException(detail=e.detail, status_code=status.HTTP_404_NOT_FOUND)