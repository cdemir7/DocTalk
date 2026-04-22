from pydantic import BaseModel
from typing import List


class ChunkItem(BaseModel):
    index: int
    content: str


class UploadResponse(BaseModel):
    fileName: str
    rawFilePath: str
    parsedFilePath: str
    chunksFilePath: str
    totalChunks: int
