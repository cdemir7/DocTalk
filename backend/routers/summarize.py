from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.models.schemas import SummarizeRequest, SummarizeResponse, SummarizeSource
from backend.services.vector_service import vector_store
from backend.services.llm_service import generate_summary

router = APIRouter(prefix="/summarize", tags=["summarize"])

# ── Limitler ──────────────────────────────────────────────────────────────────
_MAX_CHUNKS = 40          # özetleme için maksimum chunk sayısı
_MAX_CHARS  = 60_000      # özetleme için maksimum toplam karakter


@router.post("", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest) -> SummarizeResponse:
    # ── 1. Hedef doc_id listesini belirle ─────────────────────────────────────
    if request.docId:
        target_ids = {request.docId}
    elif request.docIds:
        target_ids = set(request.docIds)
    else:
        raise HTTPException(
            status_code=422,
            detail="En az bir 'docId' veya 'docIds' girilmeli.",
        )

    # ── 2. Metadata'dan chunk'ları topla ──────────────────────────────────────
    all_meta = vector_store._meta  # list[dict]
    matched = [m for m in all_meta if m["doc_id"] in target_ids]

    if not matched:
        raise HTTPException(
            status_code=404,
            detail="Belirtilen doküman(lar) bulunamadı veya henüz indekslenmedi.",
        )

    # chunk_index'e göre sırala (doğal okuma sırası)
    matched.sort(key=lambda m: (m["doc_id"], m["chunk_index"]))

    # ── 3. Limit uygula ───────────────────────────────────────────────────────
    selected: list[dict] = []
    total_chars = 0

    for m in matched:
        text = m.get("chunk_text", "")
        if not text:
            continue
        if len(selected) >= _MAX_CHUNKS:
            break
        if total_chars + len(text) > _MAX_CHARS:
            remaining = _MAX_CHARS - total_chars
            if remaining > 200: 
                truncated = dict(m)
                truncated["chunk_text"] = text[:remaining]
                selected.append(truncated)
                total_chars += remaining
            break
        selected.append(m)
        total_chars += len(text)

    # ── 4. Bağlam metnini derle ───────────────────────────────────────────────
    context_parts: list[str] = []
    for m in selected:
        label = f"[{m['doc_name']} | Parça {m['chunk_index']}]"
        context_parts.append(f"{label}\n{m['chunk_text']}")

    context = "\n\n---\n\n".join(context_parts)

    # ── 5. Özet stilini belirle ───────────────────────────────────────────────
    style = request.style or "short"
    if style not in ("short", "detailed", "bullet"):
        style = "short"

    # ── 6. Gemini'den özet üret ───────────────────────────────────────────────
    try:
        summary_text = generate_summary(context, style)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM özetleme hatası: {exc}",
        ) from exc

    # ── 7. Kaynak listesi (doküman bazında, tekrarsız) ────────────────────────
    seen_docs: dict[str, str] = {}
    for m in selected:
        if m["doc_id"] not in seen_docs:
            seen_docs[m["doc_id"]] = m["doc_name"]

    sources = [
        SummarizeSource(docId=doc_id, docName=doc_name)
        for doc_id, doc_name in seen_docs.items()
    ]

    return SummarizeResponse(summary=summary_text, sources=sources)
