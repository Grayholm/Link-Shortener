from pathlib import Path
import sys

from fastapi import FastAPI

sys.path.append(str(Path(__file__).parent.parent))

from src.api import router

app = FastAPI()

app.include_router(router)