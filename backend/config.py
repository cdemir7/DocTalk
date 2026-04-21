from dotenv import load_dotenv
import os

# .env dosyasını yükle
load_dotenv()

class Settings:
    # Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Gemini Model Ayarları
    GEMINI_LLM_MODEL: str = "gemini-2.5-flash-preview-04-17"
    GEMINI_EMBEDDING_MODEL: str = "models/text-embedding-004"
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    CHROMA_COLLECTION_NAME: str = "doctalk"
    
    # Chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "256"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "30"))
    
    # Retrieval
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Desteklenen dosya formatları
    SUPPORTED_EXTENSIONS: list = [".txt", ".pdf", ".doc", ".docx"]

# Uygulama genelinde kullanılacak tek bir settings nesnesi
settings = Settings()