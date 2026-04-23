from __future__ import annotations

from google import genai
from google.genai import types

from backend.config import settings

_SYSTEM_PROMPT = """Sen bir belge asistanısın. Kullanıcının sorularını YALNIZCA aşağıdaki belge parçalarına (bağlam) dayanarak yanıtla.

Kurallar:
1. Yalnızca verilen bağlamdaki bilgileri kullan; dışarıdan bilgi ekleme.
2. Bağlamda cevap bulamazsan: "Üzgünüm, bu bilgiyi yüklenen belgelerde bulamadım." de.
3. Cevabı Türkçe ver.
4. Cevabı kısa ve net tut; gereksiz tekrardan kaçın."""

_MODEL = "gemini-2.5-flash"

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.geminiApiKey)
    return _client


def generate_answer(context: str, question: str) -> str:
    """
    Verilen bağlam (chunk metinleri) ve soruya dayanarak Gemini'den yanıt üretir.

    context : "[doc_name | chunk_index] chunk_text ..." biçiminde birleştirilmiş metin
    question: kullanıcının ham sorusu
    """
    if not context.strip():
        return "Üzgünüm, bu soruyu yanıtlamak için yüklenen belgelerde yeterli bilgi bulamadım."

    user_content = f"BAĞLAM:\n{context}\n\nSORU: {question}"

    response = _get_client().models.generate_content(
        model=_MODEL,
        contents=user_content,
        config=types.GenerateContentConfig(
            system_instruction=_SYSTEM_PROMPT,
            temperature=0.2,
        ),
    )

    return response.text.strip()
