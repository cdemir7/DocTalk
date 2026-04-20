from fastapi import FastAPI

from backend.config import ensureDirectoriesExist
from backend.routers import upload

app = FastAPI(title="DocTalk API", version="0.1.0")

ensureDirectoriesExist()

app.include_router(upload.router)
