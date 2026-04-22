import uuid
import json
import shutil
from pathlib import Path
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config import settings
from backend.models.schemas import UploadResponse
from backend.services.chunking_service import chunkDocument
from backend.services.document_service import parseDocument

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
                detail=f"Desteklenmeyen dosya tipi: '{suffix}'. İzin verilenler: {', '.join(ALLOWED_SUFFIXES)}",
            )

        docId = uuid.uuid4().hex
        rawPath = _saveRawFile(file, docId)

        try:
            parsedPath = parseDocument(rawPath)
            chunksPath = chunkDocument(parsedPath, suffix)
        except Exception as exc:
            rawPath.unlink(missing_ok=True)
            raise HTTPException(status_code=422, detail=str(exc))

        with chunksPath.open(encoding="utf-8") as f:
            chunkCount = len(json.load(f))

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
