from fastapi import APIRouter, HTTPException

from backend.models.schemas import SummarizeRequest, SummarizeResponse

router = APIRouter(prefix="/summarize", tags=["summarize"])


@router.post("", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    if not request.docId and not request.docIds:
        raise HTTPException(status_code=422, detail="En az bir docId veya docIds girilmeli.")

    # Sprint 5'te chunk toplama → Gemini özetleme pipeline'ı buraya gelecek.
    return SummarizeResponse(
        summary=(
            "Henüz özetleme özelliği aktif değil. "
            "Sprint 5 (Özetleme + Çoklu Doküman) tamamlandığında bu alana gerçek özet gelecek."
        ),
        sources=[],
    )
