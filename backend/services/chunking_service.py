import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from langchain_text_splitters import MarkdownTextSplitter, RecursiveCharacterTextSplitter

from backend.config import settings


class TextChunker(ABC):
    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        ...


class MarkdownChunker(TextChunker):
    def __init__(self, chunkSize: int = 1000, chunkOverlap: int = 150):
        self._splitter = MarkdownTextSplitter(
            chunk_size=chunkSize,
            chunk_overlap=chunkOverlap,
        )

    def chunk(self, text: str) -> List[str]:
        return self._splitter.split_text(text)


class PlainTextChunker(TextChunker):
    def __init__(self, chunkSize: int = 1000, chunkOverlap: int = 150):
        self._splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " "],
            chunk_size=chunkSize,
            chunk_overlap=chunkOverlap,
        )

    def chunk(self, text: str) -> List[str]:
        return self._splitter.split_text(text)


_chunkers: dict[str, TextChunker] = {
    ".pdf": MarkdownChunker(),
    ".docx": MarkdownChunker(),
    ".txt": PlainTextChunker(),
}


def chunkDocument(parsedFilePath: Path, originalSuffix: str) -> Path:
    chunker = _chunkers.get(originalSuffix.lower())
    if chunker is None:
        raise ValueError(f"Desteklenmeyen dosya tipi: {originalSuffix}")

    text = parsedFilePath.read_text(encoding="utf-8")
    chunks = chunker.chunk(text)

    stem = parsedFilePath.stem.removesuffix("_parsed")
    outputPath = settings.parsedResourcesDirectory / f"{stem}_chunks.json"

    payload = [{"index": i, "content": chunk} for i, chunk in enumerate(chunks)]
    outputPath.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return outputPath
