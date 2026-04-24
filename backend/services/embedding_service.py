from __future__ import annotations

import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from backend.config import settings

_embedder: GoogleGenerativeAIEmbeddings | None = None


def _get_embedder() -> GoogleGenerativeAIEmbeddings:
    global _embedder
    if _embedder is None:
        _embedder = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-2",
            google_api_key=settings.geminiApiKey,
        )
    return _embedder

def _normalize(matrix: np.ndarray) -> np.ndarray:
    """
    Her satır vektörünü birim vektöre dönüştürür.
    """
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return matrix / norms


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Bir metin listesini embedding vektörlerine dönüştürür.

    Her metin ayrı bir API çağrısıyla embed edilir; bu sayede google-genai
    SDK'nın batch davranışından bağımsız olarak N giriş → N vektör garantisi
    sağlanır.
    """
    if not texts:
        raise ValueError("embed_texts: boş liste geçilemez.")

    empty_indices = [i for i, t in enumerate(texts) if not t or not t.strip()]
    if empty_indices:
        raise ValueError(
            f"embed_texts: {len(empty_indices)} adet boş/boşluklu metin var "
            f"(index'ler: {empty_indices[:5]}). Lütfen filtreleyin."
        )

    embedder = _get_embedder()
    vectors: list[list[float]] = []

    for text in texts:
        result = embedder.embed_documents([text])   
        if not result:
            raise ValueError(
                f"Embedding API boş sonuç döndürdü. "
                f"Metin (ilk 80 karakter): '{text[:80]}'"
            )
        vectors.append(result[0])

    matrix = np.array(vectors, dtype=np.float32) 
    return _normalize(matrix)



def embed_text(text: str) -> np.ndarray:
    """
    Tek bir sorgu metnini embedding vektörüne dönüştürür.
    """
    if not text or not text.strip():
        raise ValueError("embed_text: boş string geçilemez.")

    embedder = _get_embedder()
    raw: list[float] = embedder.embed_query(text)

    vector = np.array(raw, dtype=np.float32)
    norm = np.linalg.norm(vector)
    if norm > 0:
        vector = vector / norm
    return vector
