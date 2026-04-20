# DocTalk için Sprint Planı

## 1. Mimari ve Teknolojiler

- **LLM:** **LangChain** entegrasyonu ile **Groq API** kullanılacak. 
- **Vektör Veritabanı:** **FAISS veya ChromaDB** kullanılacak.
- **Arayüz:** *Streamlit* kullanılacak.

---

## 2. Agile Sprint Planı

### (Tamamlandı) Sprint 1: Ortam Kurulumu ve Altyapı 
**Hedef:** Projenin temel iskeletini ayağa kaldırmak.

- [x] **Gereksinim Yönetimi (Tamamlandı):**
  - Groq API hesabı oluşturulması ve API key alınması.

- [x] **Klasör Yapısı Oluşturulması (Tamamlandı):**
  - FastAPI başlangıç noktası: `backend/main.py`
  - API Endpoint'leri: `backend/routers/upload.py` (Dosya), `backend/routers/chat.py` (Sohbet)
  - Veri Modelleri: `backend/models/schemas.py` (Pydantic request/response şemaları)
  - Servis Katmanları: `services/document_service.py`, `services/chunking_service.py`, `services/vector_service.py`, `services/embedding_service.py`, `services/llm_service.py`
- [x] **Ortam Değişkenleri Yönetimi (Tamamlandı):**
  - `.env` dosyasının oluşturulması, `GROQ_API_KEY` 
- [x] **Arayüz (Streamlit) Prototipi (Tamamlandı):**
  - Kullanıcıdan dosya alan, sol panelde ayarları, sağ asıl panelde ise Chat arayüzünü gösteren giriş şablonu oluşturulması (`frontend/app.py`).

---

### (Tamamlandı) Sprint 2: Belge İşleme (Parsing & Chunking) Modülleri
**Hedef:** Kullanıcıdan gelen dosyaları temiz metinlere ayırmak ve token limitlerine uygun chunk'ları yaratmak.

- [x] **Parsing İşlemleri (`backend/services/document_service.py` & `backend/routers/upload.py`) (Tamamlandı):**
  - **PDF İşleyici (PyMuPDF4LLM):** `pymupdf4llm.to_markdown` metodu ile belgenin sayfalarındaki metinlerin ve tabloların standart Markdown formatına doğrudan çıkarılması.
  - **Word Dosyası İşleyici (docx2pdf → PyMuPDF4LLM):** `PyMuPDF4LLM` docx desteklemiyor. Bu yüzden `docx2pdf` kütüphanesi ile `.docx` dosyası önce geçici bir PDF'e dönüştürülür, ardından aynı `pymupdf4llm.to_markdown` pipeline'ından geçirilir. Böylece tüm dosya tipleri tek tip bir işlem zincirinden geçer.
  - **TXT Dosyası İşleyici:** Python'un yerleşik `open()` fonksiyonu ile `UTF-8` kodlamasında okunur; ardından gereksiz boşluklar, boş satırlar ve satır sonu karakterleri (`\r\n → \n`) normalize edilerek diğer tiplerdeki gibi tek bir ham metin string'ine dönüştürülür ve ortak pipeline'a beslenir.
- [x] **Chunking İşlemleri (`backend/services/chunking_service.py`) (Tamamlandı):**
  - **PDF / Word → Markdown Chunking:** `pymupdf4llm` çıktısı Markdown olduğu için `langchain.text_splitter.MarkdownTextSplitter` kullanılır; `#`, `##`, `###` header seviyelerine göre bağlam korunarak bölünür.
  - **TXT → Düz Metin Chunking:** TXT dosyaları Markdown header içermez; `MarkdownTextSplitter` bu dosyaları tek bir chunk olarak görür. Bu nedenle `.txt` için `langchain.text_splitter.RecursiveCharacterTextSplitter` kullanılır; ayırıcı sırası `["\n\n", "\n", ". ", " "]` şeklinde belirlenerek paragraf → cümle → kelime önceliğiyle doğal bölünme sağlanır.
  - `chunking_service.py` dosya tipini alarak yukarıdaki iki stratejiden birine yönlendiren `get_splitter(file_type)` fonksiyonu ile soyutlanır.
- [x] **Entegrasyon Testi (Sprint Çıktısı) (Tamamlandı):**
  - Projeye manuel bir PDF verilince `pymupdf4llm` ile hatasız Markdown'a dönüştüğünü, sonrasında `MarkdownTextSplitter` sayesinde anlamlı chunk'lar elde edildiğini konsolda görebilmeli.

---

### Sprint 3: ChromaDB ve RAG Mimarisi Uzlaştırma
**Hedef:** Bölünen parçaları Chromadb'ye embedding ve semantic arama modülünü devreye sokmak.

- [ ] **Embedding İşlemi:**
  - Sistemin kullanacağı yerel bir Embedding Modeli eklenmesi.
- [ ] **ChromaDB Kurulumu (`backend/services/vector_service.py`):**
  - Geçici bellekte çalışacak veya yerel bir `.chroma_db` dizininde saklanacak Chroma istemcisinin inşası.
  - Bölünen metin yığınlarının ve meta verilerinin boyutlandırılıp ChromaDB'ye eklenmesi (`vectorstore.add_documents()`).
- [ ] **Benzerlik Araması:**
  - Kullanıcıdan gelen bir test sorgusu ile DB üzerinden en ilgili `k` adet sonuç getirme metodunun kodlanması.
- [ ] **Performans İyileştirmesi:**
  - Aynı dosya defalarca yüklendiğinde tekrar embedding yapmamak için belgeden alınan Hash üzerinden Chroma'da belge kontrolü kurgulanması.

---

### Sprint 4: Groq LLM Entegrasyonu ve Streamlit Arayüz Bağlantısı
**Hedef:** Sistem parçalarını birleştirmek, Soru-Cevap deneyimini kusursuzlaştırmak ve halüsinasyon önleyici tedbirler almak.

- [ ] **Groq API Bağlantısı (`backend/services/llm_service.py` & `backend/routers/chat.py`):**
  - Langchain üzerinden `ChatGroq` wrapper'ının ayağa kaldırılması ve modelin bağlanması.
- [ ] **Prompt Mühendisliği:**
  - Modele `System Prompt` oluşturulması.
- [ ] **Soru Doğrulama ve Yanıt Motoru:**
  - Kullanıcı sorusu -> Vektörel Arama (ChromaDB) -> `Prompt + Sorular` -> Groq API (LLM) -> Yanıt yapısına büründürülmesi.
- [ ] **Streamlit UI Finalizasyonu (`frontend/app.py`):**
  - Mevcut `st.session_state` mesajlaşma altyapısına backend bağlantılarının (`fetchLlmResponse` içerisinden) yapılması.
  - LLM'den gelen cevapların ekranda gösterilmesi.
  - Yanıta ek olarak `Expand / Accordion` kullanılarak, alınan en ilgili metinlerin kaynaklarının kullanıcıya sunan kutucukların arayüze eklenmesi.