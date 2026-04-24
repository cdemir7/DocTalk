import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config import settings
from backend.models.schemas import UploadResponse, ChunkMetadata
from backend.services.chunking_service import chunkDocument
from backend.services.document_service import parseDocument
from backend.services.embedding_service import embed_texts
from backend.services.vector_service import vector_store

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt"}


def _saveRawFile(file: UploadFile, docId: str) -> Path:
    suffix = Path(file.filename).suffix.lower()
    destination = settings.rawUploadDirectory / f"{docId}{suffix}"
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return destination


@router.post("", response_model=List[UploadResponse])
async def uploadDocuments(files: List[UploadFile] = File(...)):
    results: List[UploadResponse] = []

    for file in files:
        suffix = Path(file.filename).suffix.lower()

        if suffix not in ALLOWED_SUFFIXES:
            raise HTTPException(
                status_code=415,
                detail=(
                    f"Desteklenmeyen dosya tipi: '{suffix}'. "
                    f"İzin verilenler: {', '.join(ALLOWED_SUFFIXES)}"
                ),
            )

        docId = uuid.uuid4().hex
        rawPath = _saveRawFile(file, docId)

        # ── 1. Parse + Chunk ───────────────────────────────────────────────
        try:
            parsedPath = parseDocument(rawPath)
            chunksPath = chunkDocument(parsedPath, suffix)
        except Exception as exc:
            rawPath.unlink(missing_ok=True)
            raise HTTPException(status_code=422, detail=str(exc))

        with chunksPath.open(encoding="utf-8") as f:
            chunks: list[dict] = json.load(f)

        chunkCount = len(chunks)

        # ── 2. Embedding ────────────────────────────────────────────────
        chunkTexts = [c["content"] for c in chunks]

        nonEmptyPairs = [
            (i, text) for i, text in enumerate(chunkTexts) if text and text.strip()
        ]

        if not nonEmptyPairs:
            rawPath.unlink(missing_ok=True)
            raise HTTPException(
                status_code=422,
                detail=f"'{file.filename}' dosyasından anlamlı chunk üretilemedi.",
            )

        validIndices, validTexts = zip(*nonEmptyPairs)

        try:
            vectors = embed_texts(list(validTexts))
        except Exception as exc:
            rawPath.unlink(missing_ok=True)
            raise HTTPException(
                status_code=502,
                detail=f"Embedding hatası: {exc}",
            )

        # ── 3. FAISS İndeksleme ─────────────────────────────────────────  
        now = datetime.now(timezone.utc).isoformat()
        metadatas = [
            ChunkMetadata(
                doc_id=docId,
                doc_name=file.filename,
                chunk_index=chunks[origIdx]["index"],
                chunk_text=chunks[origIdx]["content"],
                source_path=str(rawPath),
                created_at=now,
            )
            for origIdx in validIndices
        ]

        try:
            await vector_store.add_vectors(vectors, metadatas)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"FAISS indeksleme hatası: {exc}",
            )

        # ── 4. Yanıt ───────────────────────────────────────────────────────   
        results.append(
            UploadResponse(
                docId=docId,
                docName=file.filename,
                fileName=file.filename,
                rawFilePath=str(rawPath),
                parsedFilePath=str(parsedPath),
                chunksFilePath=str(chunksPath),
                totalChunks=chunkCount,
            )
        )

    return results
