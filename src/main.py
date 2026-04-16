from contextlib import asynccontextmanager
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

sys.path.append(str(Path(__file__).parent.parent))

from src.api import router
from src.exceptions import AppError
from src.redis_config import redis_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await redis_manager.ping()
        logger.info("Redis connected")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise

    yield

    await redis_manager.close()

app = FastAPI(lifespan=lifespan)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    logger.error("App error on %s: %s", request.url.path, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

app.include_router(router)
