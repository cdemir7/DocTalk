from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    geminiApiKey: str = Field(
        default="",
        validation_alias="GEMINI_API_KEY",
    )

    rawUploadDirectory: Path = Path("uploads/raw")
    parsedResourcesDirectory: Path = Path("uploads/parsed")
    faissDirectory: Path = Path("uploads/faiss")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()


def ensureDirectoriesExist() -> None:
    settings.rawUploadDirectory.mkdir(parents=True, exist_ok=True)
    settings.parsedResourcesDirectory.mkdir(parents=True, exist_ok=True)
    settings.faissDirectory.mkdir(parents=True, exist_ok=True)
