from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    groqApiKey: str = ""
    rawUploadDirectory: Path = Path("uploads/raw")
    parsedResourcesDirectory: Path = Path("uploads/parsed")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()


def ensureDirectoriesExist() -> None:
    settings.rawUploadDirectory.mkdir(parents=True, exist_ok=True)
    settings.parsedResourcesDirectory.mkdir(parents=True, exist_ok=True)
