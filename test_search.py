from dotenv import load_dotenv

load_dotenv()

from backend.services.embedding_service import embed_text
from backend.services.vector_service import vector_store

def test_search(query: str, top_k: int = 3):
    print(f"\n--- Soru: '{query}' ---")
    
    print("Soru vektöre dönüştürülüyor...")
    query_vector = embed_text(query)
    
    print(f"FAISS'te en yakın {top_k} parça aranıyor...\n")
    hits = vector_store.search(query_vector, k=top_k)
    
    if not hits:
        print("Sonuç bulunamadı. Lütfen önce bir dosya yüklediğinizden emin olun.")
        return

    for i, hit in enumerate(hits, 1):
        print(f"--- Sonuç {i} (Skor: {hit.score:.4f}) ---")
        print(f"Dosya: {hit.metadata.doc_name} (Chunk: {hit.metadata.chunk_index})")
        
        content_preview = hit.metadata.chunk_text[:150].replace('\n', ' ')
        print(f"İçerik: {content_preview}...\n")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="FAISS Vektör Araması Testi")
    parser.add_argument("query", type=str, help="Aramak istediğiniz metin/soru")
    parser.add_argument("--k", type=int, default=3, help="Döndürülecek sonuç sayısı (varsayılan: 3)")
    
    args = parser.parse_args()
    
    test_search(args.query, top_k=args.k)

