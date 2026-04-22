from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import ensureDirectoriesExist
from backend.routers import upload, chat, summarize

app = FastAPI(title="DocTalk API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ensureDirectoriesExist()

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(summarize.router)
