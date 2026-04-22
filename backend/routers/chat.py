from fastapi import APIRouter

from backend.models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Sprint 4'te RAG pipeline (embed_text → FAISS search → Gemini generate) buraya gelecek.
    return ChatResponse(
        answer=(
            "Henüz sohbet özelliği aktif değil. "
            "Sprint 4 (RAG Chat API) tamamlandığında bu alana gerçek cevaplar gelecek."
        ),
        sources=[],
    )
