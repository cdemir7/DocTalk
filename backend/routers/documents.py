from fastapi import APIRouter, HTTPException
from typing import List

from backend.config import settings
from backend.models.schemas import DocumentInfo
from backend.services.vector_service import vector_store

router = APIRouter(prefix="/documents", tags=["documents"])

@router.get("", response_model=List[DocumentInfo])
async def listDocuments():
    """
    Disk'teki FAISS meta.json'dan benzersiz dokümanları döndürür.
    Uygulama yeniden başlasa veya sayfa yenilense bile liste korunur.
    """
    raw_docs = vector_store.list_documents()
    return [
        DocumentInfo(
            docId=d["doc_id"],
            docName=d["doc_name"],
            fileName=d["doc_name"],
            totalChunks=d["total_chunks"],
            createdAt=d["created_at"],
        )
        for d in raw_docs
    ]



@router.delete("/{doc_id}", status_code=204)
async def deleteDocument(doc_id: str):
    """
    Bir dokümanı tamamen siler:
    1. uploads/raw/ → ham dosya
    2. uploads/parsed/ → _parsed.md ve _chunks.json
    3. FAISS index + meta.json → vektörler ve metadata
    """
    removed = await vector_store.delete_by_doc_id(doc_id)

    if removed == 0:
        raise HTTPException(
            status_code=404,
            detail=f"'{doc_id}' ID'li doküman bulunamadı veya zaten silinmiş.",
        )

    _delete_doc_files(doc_id)


def _delete_doc_files(doc_id: str) -> None:
    """
    uploads/raw/ ve uploads/parsed/ altındaki doc_id'ye ait dosyaları siler.
    Dosya bulunamazsa sessizce geçer (already-deleted safe).
    """
    for suffix in (".pdf", ".docx", ".txt"):
        raw = settings.rawUploadDirectory / f"{doc_id}{suffix}"
        if raw.exists():
            raw.unlink()
            break

    parsed = settings.parsedResourcesDirectory / f"{doc_id}_parsed.md"
    parsed.unlink(missing_ok=True)

    chunks = settings.parsedResourcesDirectory / f"{doc_id}_chunks.json"
    chunks.unlink(missing_ok=True)
