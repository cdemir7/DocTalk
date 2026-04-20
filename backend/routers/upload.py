import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.config import settings
from backend.models.schemas import UploadResponse
from backend.services.chunking_service import chunkDocument
from backend.services.document_service import parseDocument

router = APIRouter(prefix="/upload", tags=["upload"])

ALLOWED_SUFFIXES = {".pdf", ".docx", ".txt"}


def _saveRawFile(file: UploadFile) -> Path:
    originalPath = Path(file.filename)
    suffix = originalPath.suffix.lower()
    uniqueName = f"{uuid.uuid4().hex}{suffix}"
    destination = settings.rawUploadDirectory / uniqueName
    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return destination


@router.post("", response_model=UploadResponse)
async def uploadDocument(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()

    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=415,
            detail=f"Desteklenmeyen dosya tipi: '{suffix}'. İzin verilenler: {', '.join(ALLOWED_SUFFIXES)}",
        )

    rawPath = _saveRawFile(file)

    try:
        parsedPath = parseDocument(rawPath)
        chunksPath = chunkDocument(parsedPath, suffix)
    except Exception as exc:
        rawPath.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(exc))

    chunkCount = 0
    import json
    with chunksPath.open(encoding="utf-8") as f:
        chunkCount = len(json.load(f))

    return UploadResponse(
        fileName=file.filename,
        rawFilePath=str(rawPath),
        parsedFilePath=str(parsedPath),
        chunksFilePath=str(chunksPath),
        totalChunks=chunkCount,
    )
