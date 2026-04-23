from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.models.schemas import ChatRequest, ChatResponse, Source
from backend.services.embedding_service import embed_text
from backend.services.vector_service import vector_store
from backend.services.llm_service import generate_answer

router = APIRouter(prefix="/chat", tags=["chat"])

_MAX_CONTEXT_CHARS = 15_000
_SNIPPET_LENGTH = 300


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="Soru boş olamaz.")

    top_k = max(1, request.topK or 5)

    # ── 1. Soru vektörü ───────────────────────────────────────────────────────
    try:
        query_vector = embed_text(question)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Embedding hatası: {exc}") from exc

    # ── 2. FAISS araması ──────────────────────────────────────────────────────
    # top_k'dan fazla al; filtreleme sonrası yeterlisi kalır.
    raw_hits = vector_store.search(query_vector, k=top_k * 3)

    # ── 3. docIds filtresi ────────────────────────────────────────────────────
    if request.docIds:
        allowed = set(request.docIds)
        raw_hits = [h for h in raw_hits if h.metadata.doc_id in allowed]

    # ── 4. Deduplikasyon (aynı chunk'ı tekrar alma) ───────────────────────────
    seen: set[tuple[str, int]] = set()
    unique_hits = []
    for hit in raw_hits:
        key = (hit.metadata.doc_id, hit.metadata.chunk_index)
        if key not in seen:
            seen.add(key)
            unique_hits.append(hit)
        if len(unique_hits) >= top_k:
            break

    # ── 5. Bağlam derleme ─────────────────────────────────────────────────────
    # Her chunk "[doc_name | chunk_index]\nchunk_text" etiketiyle eklenir.
    # Toplam karakter limiti aşılırsa chunk eklenmez (token limitine takılmamak için).
    context_parts: list[str] = []
    total_chars = 0
    hits_for_source = []

    for hit in unique_hits:
        label = f"[{hit.metadata.doc_name} | Parça {hit.metadata.chunk_index}]"
        chunk_block = f"{label}\n{hit.metadata.chunk_text}"

        if total_chars + len(chunk_block) > _MAX_CONTEXT_CHARS:
            break

        context_parts.append(chunk_block)
        total_chars += len(chunk_block)
        hits_for_source.append(hit)

    context = "\n\n---\n\n".join(context_parts)

    # ── 6. LLM cevabı ─────────────────────────────────────────────────────────
    try:
        answer = generate_answer(context, question)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM hatası: {exc}") from exc

    # ── 7. Kaynak listesi ─────────────────────────────────────────────────────
    sources = [
        Source(
            docId=hit.metadata.doc_id,
            docName=hit.metadata.doc_name,
            chunkIndex=hit.metadata.chunk_index,
            snippet=hit.metadata.chunk_text[:_SNIPPET_LENGTH],
            score=round(hit.score, 4),
        )
        for hit in hits_for_source
    ]

    return ChatResponse(answer=answer, sources=sources)
