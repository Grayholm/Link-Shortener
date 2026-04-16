from contextlib import asynccontextmanager
from pathlib import Path
import sys
import logging

logger = logging.getLogger(__name__)

from fastapi import FastAPI

sys.path.append(str(Path(__file__).parent.parent))

from src.api import router
from src.redis_config import redis_manager

app = FastAPI()

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

app.include_router(router)