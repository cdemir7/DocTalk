from __future__ import annotations

import asyncio
import json
from pathlib import Path

import faiss
import numpy as np

from backend.config import settings
from backend.models.schemas import ChunkMetadata, SearchHit

def _index_path() -> Path:
    return settings.faissDirectory / "index.faiss"


def _meta_path() -> Path:
    return settings.faissDirectory / "meta.json"

class VectorStore:
    """FAISS IndexFlatIP üzerinde vektör ekle / ara / kaydet / yükle."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._meta: list[dict] = []
        self._index: faiss.IndexFlatIP | None = None
        self._dim: int | None = None
        self._try_load()

    def _try_load(self) -> None:
        """Disk'te index varsa yükle; yoksa boş bırak (ilk eklemede oluşur)."""
        idx_path = _index_path()
        meta_path = _meta_path()

        if idx_path.exists() and meta_path.exists():
            self._index = faiss.read_index(str(idx_path))
            self._dim = self._index.d
            with meta_path.open(encoding="utf-8") as f:
                self._meta = json.load(f)
            print(
                f"[VectorStore] Disk'ten yüklendi: "
                f"{self._index.ntotal} vektör, dim={self._dim}"
            )
        else:
            print("[VectorStore] Disk'te index bulunamadı; ilk eklemede oluşturulacak.")

    def _save(self) -> None:
        """FAISS index ve meta.json'ı diske yazar."""
        if self._index is None:
            return
        faiss.write_index(self._index, str(_index_path()))
        with _meta_path().open("w", encoding="utf-8") as f:
            json.dump(self._meta, f, ensure_ascii=False, indent=2)

    def _init_index(self, dim: int) -> None:
        self._dim = dim
        self._index = faiss.IndexFlatIP(dim)
        print(f"[VectorStore] Yeni IndexFlatIP oluşturuldu: dim={dim}")

    async def add_vectors(
        self,
        vectors: np.ndarray,
        metadatas: list[ChunkMetadata],
    ) -> None:
        """
        Normalize edilmiş vektörleri FAISS index'e ve meta.json'a ekler.
        """
        if len(vectors) != len(metadatas):
            raise ValueError(
                f"add_vectors: vektör sayısı ({len(vectors)}) "
                f"ile metadata sayısı ({len(metadatas)}) eşleşmiyor."
            )

        if vectors.ndim != 2:
            raise ValueError(
                f"add_vectors: vectors 2 boyutlu olmalı, mevcut: {vectors.ndim}D"
            )

        vectors = np.ascontiguousarray(vectors, dtype=np.float32)

        async with self._lock:
            if self._index is None:
                self._init_index(vectors.shape[1])
            elif vectors.shape[1] != self._dim:
                raise ValueError(
                    f"add_vectors: vektör boyutu {vectors.shape[1]} != "
                    f"mevcut index boyutu {self._dim}"
                )

            self._index.add(vectors)
            self._meta.extend([m.model_dump() for m in metadatas])
            self._save()

        print(
            f"[VectorStore] {len(vectors)} vektör eklendi. "
            f"Toplam: {self._index.ntotal}"
        )

    def search(self, query_vector: np.ndarray, k: int = 5) -> list[SearchHit]:
        """
        Sorgu vektörüne en yakın k chunk'ı döndürür.
        """
        if self._index is None or self._index.ntotal == 0:
            return []

        query_vector = np.ascontiguousarray(
            query_vector.reshape(1, -1), dtype=np.float32
        )

        effective_k = min(k, self._index.ntotal)
        scores, indices = self._index.search(query_vector, effective_k)

        hits: list[SearchHit] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            meta_dict = self._meta[idx]
            hits.append(
                SearchHit(
                    score=float(score),
                    metadata=ChunkMetadata(**meta_dict),
                )
            )
        return hits

    def list_documents(self) -> list[dict]:
        """
        meta.json'dan benzersiz dokümanları, chunk sayılarıyla birlikte döndürür.
        Dönüş: [{doc_id, doc_name, total_chunks, created_at}, ...]
        """
        seen: dict[str, dict] = {}
        for entry in self._meta:
            doc_id = entry["doc_id"]
            if doc_id not in seen:
                seen[doc_id] = {
                    "doc_id": doc_id,
                    "doc_name": entry["doc_name"],
                    "created_at": entry["created_at"],
                    "total_chunks": 0,
                }
            seen[doc_id]["total_chunks"] += 1
        return list(seen.values())

    async def delete_by_doc_id(self, doc_id: str) -> int:
        """
        Verilen doc_id'ye ait tüm vektörleri ve metadata kayıtlarını siler.
        FAISS index'i kalan vektörlerle yeniden inşa eder.
        """
        async with self._lock:
            if self._index is None or self._index.ntotal == 0:
                return 0

            keep_indices = [
                i for i, m in enumerate(self._meta) if m["doc_id"] != doc_id
            ]
            removed_count = self._index.ntotal - len(keep_indices)

            if removed_count == 0:
                return 0

            all_vectors = np.array(
                [self._index.reconstruct(i) for i in range(self._index.ntotal)],
                dtype=np.float32,
            )

            kept_meta = [self._meta[i] for i in keep_indices]

            self._index = faiss.IndexFlatIP(self._dim)
            if keep_indices:
                kept_vectors = all_vectors[keep_indices]
                self._index.add(kept_vectors)

            self._meta = kept_meta
            self._save()

        print(
            f"[VectorStore] doc_id={doc_id} silindi: {removed_count} vektör. "
            f"Kalan: {self._index.ntotal}"
        )
        return removed_count

    @property
    def total_vectors(self) -> int:
        return self._index.ntotal if self._index is not None else 0

vector_store = VectorStore()
