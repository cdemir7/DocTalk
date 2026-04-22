from pydantic import BaseModel
from typing import List, Optional


class ChunkItem(BaseModel):
    index: int
    content: str


class UploadResponse(BaseModel):
    docId: str
    docName: str
    fileName: str
    rawFilePath: str
    parsedFilePath: str
    chunksFilePath: str
    totalChunks: int


class Source(BaseModel):
    docId: str
    docName: str
    chunkIndex: int
    snippet: str
    score: Optional[float] = None


class ChatRequest(BaseModel):
    question: str
    topK: Optional[int] = 5
    docIds: Optional[List[str]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


class SummarizeRequest(BaseModel):
    docId: Optional[str] = None
    docIds: Optional[List[str]] = None
    style: Optional[str] = "short"


class SummarizeSource(BaseModel):
    docId: str
    docName: str


class SummarizeResponse(BaseModel):
    summary: str
    sources: List[SummarizeSource]
