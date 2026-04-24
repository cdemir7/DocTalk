from __future__ import annotations

import time
import logging
from google import genai
from google.genai import types

from backend.config import settings

logger = logging.getLogger(__name__)

# ── Prompt tanımları ──────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """Sen bir belge asistanısın. Kullanıcının sorularını YALNIZCA aşağıdaki belge parçalarına (bağlam) dayanarak yanıtla.

Kurallar:
1. Yalnızca verilen bağlamdaki bilgileri kullan; dışarıdan bilgi ekleme.
2. Bağlamda cevap bulamazsan: "Üzgünüm, bu bilgiyi yüklenen belgelerde bulamadım." de.
3. Cevabı Türkçe ver.
4. Cevabı kısa ve net tut; gereksiz tekrardan kaçın."""

_SUMMARY_PROMPTS: dict[str, str] = {
    "short": """Sen bir belge özetleme asistanısın.
Aşağıdaki belge içeriğini YALNIZCA 3-6 cümle ile özetle.
Özet Türkçe olmalı, ana fikri net aktarmalı ve gereksiz ayrıntıdan kaçınmalıdır.""",

    "detailed": """Sen bir belge analiz asistanısın.
Aşağıdaki belge içeriğini kapsamlı biçimde özetle. Yanıtını şu yapıda ver:

**Ana Konu:** (1-2 cümle)

**Temel Noktalar:** (her biri 1-2 cümle, 3-6 madde)

**Sonuç / Genel Değerlendirme:** (2-3 cümle)

Tüm yanıt Türkçe olmalıdır.""",

    "bullet": """Sen bir belge özetleme asistanısın.
Aşağıdaki belge içeriğindeki EN ÖNEMLİ 5-10 noktayı madde madde listele.
Her madde kısa ve net olsun (en fazla 2 cümle).
Çıktı formatı:
- Madde 1
- Madde 2
...
Tüm yanıt Türkçe olmalıdır.""",
}

# ── Model sırası (birincil başarısız olursa sıradakine geç) ───────────────────
_MODEL_CHAIN = [
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]

# ── Retry ayarları ────────────────────────────────────────────────────────────
_MAX_RETRIES    = 3   # her model için maksimum deneme
_RETRY_BASE_SEC = 2   # ilk bekleme süresi (saniye); her denemede 2x artar

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.geminiApiKey)
    return _client


def _is_retryable(exc: Exception) -> bool:
    """503 UNAVAILABLE veya 429 RESOURCE_EXHAUSTED hatalarını retry'a uygun say."""
    msg = str(exc).upper()
    return "503" in msg or "UNAVAILABLE" in msg or "429" in msg or "RESOURCE_EXHAUSTED" in msg


def _generate_with_retry(
    *,
    user_content: str,
    system_instruction: str,
    temperature: float,
) -> str:
    """
    Model zincirini dener. Her model için _MAX_RETRIES kadar yeniden dener.
    Tüm modeller ve denemeler tükenirse son hatayı yükseltir.
    """
    last_exc: Exception | None = None

    for model in _MODEL_CHAIN:
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = _get_client().models.generate_content(
                    model=model,
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=temperature,
                    ),
                )
                if model != _MODEL_CHAIN[0]:
                    logger.info("[LLM] Yanıt %s modelinden alındı.", model)
                return response.text.strip()

            except Exception as exc:
                last_exc = exc
                if _is_retryable(exc):
                    wait = _RETRY_BASE_SEC * (2 ** (attempt - 1))  # 2s, 4s, 8s
                    logger.warning(
                        "[LLM] %s | model=%s deneme=%d/%d — %ds bekleniyor. Hata: %s",
                        "503/429", model, attempt, _MAX_RETRIES, wait, exc,
                    )
                    time.sleep(wait)
                else:
                    logger.error("[LLM] Tekrar denenemeyen hata (model=%s): %s", model, exc)
                    break  

    raise last_exc  


# ── Public API ────────────────────────────────────────────────────────────────

def generate_answer(context: str, question: str) -> str:
    """
    Verilen bağlam ve soruya dayanarak Gemini'den yanıt üretir.
    503/429 hatalarında otomatik yeniden dener; gerekirse yedek modele geçer.
    """
    if not context.strip():
        return "Üzgünüm, bu soruyu yanıtlamak için yüklenen belgelerde yeterli bilgi bulamadım."

    return _generate_with_retry(
        user_content=f"BAĞLAM:\n{context}\n\nSORU: {question}",
        system_instruction=_SYSTEM_PROMPT,
        temperature=0.2,
    )


def generate_summary(context: str, style: str = "short") -> str:
    """
    Yüklenen belge chunk'larından stil bazlı özet üretir.
    503/429 hatalarında otomatik yeniden dener; gerekirse yedek modele geçer.

    style: 'short' | 'detailed' | 'bullet'
    """
    if not context.strip():
        return "Üzgünüm, özetlemek için belge içeriği bulunamadı."

    system_prompt = _SUMMARY_PROMPTS.get(style, _SUMMARY_PROMPTS["short"])

    return _generate_with_retry(
        user_content=f"BELGE İÇERİĞİ:\n{context}",
        system_instruction=system_prompt,
        temperature=0.3,
    )
