# DocTalk için Sprint Planı

## 1. Mimari ve Teknolojiler

- **Backend (API):** **FastAPI** 
- **LLM:** **Google Gemini**
- **Embedding:** **Google Gemini Embeddings** 
  - **FAISS ile kullanım:** cosine similarity için embedding’ler normalize edilerek `IndexFlatIP` (inner product) ile aranır.
- **Vektör Veritabanı:** **FAISS** 
  - **Persist yaklaşımı:** `index.faiss` + metadata (`meta.json`) ile disk üzerinde kalıcı kayıt.
- **Arayüz:** **React**
  - **Minimum UI:** Dosya yükleme + chat ekranı + özetleme butonu.

---

## 2. Agile Sprint Planı

### (Tamamlandı) Sprint 1: Ortam Kurulumu ve Altyapı 
**Hedef:** Projenin temel iskeletini ayağa kaldırmak.

- [x] **Gereksinim Yönetimi (Tamamlandı):**
  - Google Gemini erişimi ve API key alınması.

- [x] **Klasör Yapısı Oluşturulması (Tamamlandı):**
  - FastAPI başlangıç noktası: `backend/main.py`
  - API Endpoint'leri: `backend/routers/upload.py` (Dosya), `backend/routers/chat.py` (Sohbet)
  - Veri Modelleri: `backend/models/schemas.py` (Pydantic request/response şemaları)
  - Servis Katmanları: `services/document_service.py`, `services/chunking_service.py`, `services/vector_service.py`, `services/embedding_service.py`, `services/llm_service.py`
- [x] **Ortam Değişkenleri Yönetimi (Tamamlandı):**
  - `.env` dosyasının oluşturulması, `GEMINI_API_KEY`

---

### (Tamamlandı) Sprint 2: Belge İşleme (Parsing & Chunking) Modülleri
**Hedef:** Kullanıcıdan gelen dosyaları temiz metinlere ayırmak ve token limitlerine uygun chunk'ları yaratmak.

- [x] **Parsing İşlemleri (`backend/services/document_service.py` & `backend/routers/upload.py`) (Tamamlandı):**
  - **PDF İşleyici (PyMuPDF4LLM):** `pymupdf4llm.to_markdown` metodu ile belgenin sayfalarındaki metinlerin ve tabloların standart Markdown formatına doğrudan çıkarılması.
  - **Word Dosyası İşleyici (DOCX):** `.docx` dosyası `python-docx` ile okunur; boş olmayan paragraflar alınır ve metin `\\n\\n` ile birleştirilerek tek bir ham metin çıktısı üretilir.
  - **TXT Dosyası İşleyici:** Python'un yerleşik `open()` fonksiyonu ile `UTF-8` kodlamasında okunur; ardından gereksiz boşluklar, boş satırlar ve satır sonu karakterleri (`\r\n → \n`) normalize edilerek diğer tiplerdeki gibi tek bir ham metin string'ine dönüştürülür ve ortak pipeline'a beslenir.
- [x] **Chunking İşlemleri (`backend/services/chunking_service.py`) (Tamamlandı):**
  - **PDF / Word → Markdown Chunking:** `pymupdf4llm` çıktısı Markdown olduğu için `langchain.text_splitter.MarkdownTextSplitter` kullanılır; `#`, `##`, `###` header seviyelerine göre bağlam korunarak bölünür.
  - **TXT → Düz Metin Chunking:** TXT dosyaları Markdown header içermez; `MarkdownTextSplitter` bu dosyaları tek bir chunk olarak görür. Bu nedenle `.txt` için `langchain.text_splitter.RecursiveCharacterTextSplitter` kullanılır; ayırıcı sırası `["\n\n", "\n", ". ", " "]` şeklinde belirlenerek paragraf → cümle → kelime önceliğiyle doğal bölünme sağlanır.
  - `chunking_service.py` dosya tipini alarak yukarıdaki iki stratejiden birine yönlendiren `get_splitter(file_type)` fonksiyonu ile soyutlanır.
- [x] **Entegrasyon Testi (Sprint Çıktısı) (Tamamlandı):**
  - Projeye manuel bir PDF verilince `pymupdf4llm` ile hatasız Markdown'a dönüştüğünü, sonrasında `MarkdownTextSplitter` sayesinde anlamlı chunk'lar elde edildiğini konsolda görebilmeli.

---

### Sprint 3: FAISS + Gemini Embedding + Indexleme (RAG altyapısı)
**Hedef (basit anlatım):** Sprint 2’de “metne çevirip parçaladığımız (chunk)” içerikleri, bilgisayarın “anlam benzerliği” ile arayabilmesi için sayısal vektörlere (embedding) çeviriyoruz. Sonra bu vektörleri **FAISS**’te indeksleyip disk’e kaydediyoruz ki uygulama kapanıp açılsa bile “doküman hafızası” kaybolmasın.

**Bu sprint sonunda kullanıcı açısından ne değişir?**
- Kullanıcı doküman yükler.
- Sistem bu dokümanı “arama yapılabilir” hale getirir.
- Sonraki sprintte gelecek `/chat` için zemin hazır olur (çünkü artık “soruya en yakın parçaları bulabiliyoruz”).

#### 3.1. Veri akışı 
- **Upload** → dosya metne çevrilir → **chunk listesi** oluşur  
- Her chunk → **embedding** (sayısal vektör)  
- Vektörler → **FAISS index** içine eklenir  
- Chunk’ın “kimlik bilgileri” → **metadata** olarak ayrıca saklanır (hangi dosya, hangi parça, metnin kendisi gibi)

#### 3.2. Embedding servisi (`backend/services/embedding_service.py`)
**Neyi yapacak?** “Metin listesi” alıp “vektör listesi” döndürecek.

- [ ] **API tasarımı**
  - `embed_texts(texts: list[str]) -> np.ndarray`
  - (opsiyonel) `embed_text(text: str) -> np.ndarray` (tek sorgu için)
- [ ] **Model yükleme ve performans**
  - Model: **Gemini Embeddings** (Google GenAI)
  - İstemci uygulama açılışında bir kere hazırlanmalı (her çağrıda yeniden yaratılmamalı).
- [ ] **Vektör standardı**
  - `float32`
  - Cosine benzerliği için **normalize** (her vektörün uzunluğu 1 olacak şekilde)
- [ ] **Hata dayanıklılığı**
  - Boş string’leri filtrele/atla veya anlamlı hata üret.

**Kabul kriterleri (DoD)**
- 10 chunk için çıktı boyutu **(10, D)** ve `dtype=float32`.
- Aynı metin 2 kez embed edilince hata çıkmadan çalışıyor.
- (Bonus) Normalize kontrolü: her vektör için \( \|v\| \approx 1 \).

#### 3.3. FAISS vektör servisi (`backend/services/vector_service.py`)
**Neyi yapacak?** Vektörleri “hızlı benzerlik araması” için saklayacak ve sorgu vektörüyle “en yakın k parça”yı bulacak.

- [ ] **Index yapısı**
  - Cosine için pratik yaklaşım: embedding’ler normalize edilir, FAISS’te `IndexFlatIP` (inner product) kullanılır.
- [ ] **Temel fonksiyonlar**
  - `add_vectors(vectors, metadatas)`  
    - aynı sırada gelen `vectors[i]` ile `metadatas[i]` eşleşmeli
  - `search(query_vector, k) -> list[SearchHit]`  
    - skor + metadata döndürmeli
- [ ] **Persist (kalıcılık)**
  - FAISS: `uploads/faiss/index.faiss`
  - Metadata: başlangıç için `uploads/faiss/meta.json` (ileri aşamada `sqlite`’a geçilebilir)
- [ ] **Metadata minimum alanlar**
  - `doc_id`: sistem içi ID (UUID önerilir)
  - `doc_name`: kullanıcıya gösterilecek dosya adı
  - `chunk_index`: o dokümandaki sıra numarası
  - `chunk_text`: parça metni (RAG bağlamı için lazım)
  - `source_path` (veya `original_filename`)
  - `created_at`

**Kabul kriterleri (DoD)**
- Uygulama kapanıp açılınca index + metadata diskten yükleniyor.
- `search()` sonucu hem skor hem doğru `doc_name/chunk_index` ile geliyor.
- 2 farklı doküman yüklenip indekslenince aramada iki dokümandan da hit gelebiliyor.

#### 3.4. Upload akışına indexleme ekleme (`backend/routers/upload.py`)
**Neyi yapacak?** “Parse + chunk” sonucunu alıp embedding/indexleme pipeline’ına sokacak.

- [ ] **Çoklu dosya upload**
  - İstek: `files: list[UploadFile]`
  - Her dosya için: parse → chunk → embedding → faiss add
- [ ] **Doküman kimliği yönetimi**
  - Her upload edilen dosya için `doc_id` üret ve tüm chunk metadata’sına yaz.
- [ ] **İndeksleme raporu döndürme**
  - Yanıt: her doc için `doc_id`, `doc_name`, `chunk_count` (minimum)

**Kabul kriterleri (DoD)**
- 2 dosya yüklendiğinde toplam chunk sayısı kadar vektör indeksleniyor.
- Yanıtta her dosya için `doc_id` ve `chunk_count` görülüyor.

---

### Sprint 4: RAG Chat API + Gemini LLM + Kaynak Gösterme
**Hedef (basit anlatım):** Kullanıcı bir soru sorunca sistem önce “dokümanlardan bu soruyla en alakalı yerleri” bulacak (retrieve), sonra bu parçaları Gemini LLM’e “bağlam” olarak verip yanıt üretecek (generate). En önemli kısım: **cevabın hangi parçaya dayandığını kaynak olarak döndürmek**.

**Bu sprint sonunda kullanıcı açısından ne değişir?**
- Kullanıcı `/chat` ile soru sorar.
- Sistem cevap verir ve “bu cevap şuradaki dokümanın şu kısmına dayanıyor” diye kaynak gösterir.

#### 4.1. Chat endpoint sözleşmesi (`backend/routers/chat.py`)
- [ ] **İstek (request)**
  - `question`: string (zorunlu)
  - `top_k`: int (opsiyonel, default 4-6)
  - `doc_ids`: list[str] (opsiyonel; verildiyse sadece bu dokümanlarda aransın)
- [ ] **Yanıt (response)**
  - `answer`: string
  - `sources`: liste
    - `doc_id`, `doc_name`, `chunk_index`
    - `snippet`: kullanıcıya gösterilecek kısa alıntı (örn. ilk 200-400 karakter)
    - (opsiyonel) `score`

**Kabul kriterleri (DoD)**
- `/chat` her çalıştığında `answer` ile birlikte **en az 1** `sources` elemanı döndürür (top_k>0 iken).
- `doc_ids` verilince sadece o dokümanlardan kaynak döner.

#### 4.2. Retrieve (arama) adımı: “Soru → en alakalı chunk’lar”
- [ ] **Soru embedding’i**
  - `embedding_service.embed_text(question)` ile tek vektör üret.
- [ ] **FAISS araması**
  - `vector_service.search(query_vector, k=top_k)` ile hit’leri al.
- [ ] **Sıralama ve filtreleme**
  - skorla sırala (FAISS zaten döner)
  - çok benzer/aynı chunk tekrarlarını engelle (basit deduplikasyon)

**Kabul kriterleri (DoD)**
- `top_k` artırılınca dönen kaynak sayısı artar veya değişir (gözlemlenebilir fark).

#### 4.3. Context assembly: “LLM’e verilecek bağlamı derleme”
Yeni başlayanlar için kritik nokta: LLM “tüm dokümanı” değil, sadece seçilen chunk’ları görür. Bu yüzden bağlamı düzgün paketlemek gerekir.

- [ ] **Bağlam formatı**
  - Her chunk’ı şu bilgiyle etiketle:
    - `[doc_name | chunk_index] chunk_text`
- [ ] **Limitler**
  - `max_chars` veya `max_chunks` gibi sınır koy (LLM token limitine takılmamak için)

**Kabul kriterleri (DoD)**
- Çok uzun dokümanlarda bile `/chat` 413/timeout gibi hatalara düşmeden çalışır (sınırlar devrede).

#### 4.4. LLM servisi (`backend/services/llm_service.py`)
- [ ] **Gemini entegrasyonu**
  - LangChain Gemini chat modeli veya direkt Google GenAI istemcisi ile `generate_answer(context, question)`.
- [ ] **Prompt prensipleri**
  - “Sadece verilen bağlama dayan.”
  - “Bağlamda yoksa açıkça ‘belgelerde bulamadım’ de.”
  - “Cevabı kısa ve net ver; sonunda kaynakları `sources` alanından döndüreceğiz (modelden kaynak formatı istemeyebiliriz).”

**Kabul kriterleri (DoD)**
- Bağlam dışı sorularda uydurma yapmadan “bulamadım” tarzı kontrollü yanıt verir.
- Yanıtlar Türkçe ve anlaşılırdır (doküman Türkçe ise).

---

### Sprint 5: Özetleme + Çoklu Dokümandan Birleşik Cevap
**Hedef (basit anlatım):** İki ayrı yetenek ekliyoruz:
- **Özetleme**: Dokümanın (veya birden fazla dokümanın) kısa, anlaşılır özetini üretmek.
- **Birleşik cevap (multi-doc)**: Soru tek bir dokümanda değil birkaç dokümanda dağınıksa, sistem bunları birlikte değerlendirip tek cevap üretmek.

#### 5.1. Özetleme endpoint’i (`POST /summarize`)
- [ ] **İstek modları**
  - **Tek doküman**: `doc_id`
  - **Çoklu doküman**: `doc_ids: list[str]`
  - (opsiyonel) `style`: `"short" | "detailed" | "bullet"` gibi
- [ ] **Yanıt**
  - `summary`: string
  - `sources`: (özetin hangi dokümanlardan üretildiği)

#### 5.2. Özetleme stratejisi (başlangıç için basit ve güvenli)

Yeni başlayanlar için önemli not: “özetleme”, chat’ten farklı olarak genelde **tüm dokümanı** kapsamak ister. Ama tüm metni tek seferde LLM’e göndermek token limitine takılabilir. Bu yüzden ilk sürümde güvenli bir strateji seçiyoruz.

- [ ] **Girdi toplama**
  - Tek doküman: o `doc_id`’ye ait tüm chunk’ları (metadata’dan) al.
  - Çoklu doküman: seçilen tüm `doc_ids` için chunk’ları birleştir.
- [ ] **Sınır koyma (token/uzunluk yönetimi)**
  - Basit yaklaşım: en fazla `max_chunks_for_summary` (örn. 20-40) ve/veya `max_chars_for_summary` (örn. 30k-60k char).
  - Eğer doküman çok büyükse: chunk’lardan örnekle (ilk/son + başlık yoğun bölümler) veya “retrieve ile özet” (opsiyonel gelişmiş).
- [ ] **Özet prompt’u**
  - Çıktı formatı net olsun:
    - Kısa özet (3-6 cümle)
    - Madde madde önemli noktalar
    - (Opsiyonel) Terminoloji / ana kavramlar

**Kabul kriterleri (DoD)**
- Tek doküman özeti üretildiğinde `summary` dolu gelir ve `sources` en az o dokümanı içerir.
- 2 doküman seçilince tek bir birleşik özet döner; `sources` doküman bazında listelenir.

#### 5.3. Birleşik cevap (multi-doc RAG) davranışı
Sprint 4’teki `/chat` RAG akışını “birden fazla dokümanda birlikte arama” yapacak şekilde netleştiriyoruz.

- [ ] **Doküman filtreleme**
  - `/chat` isteğinde `doc_ids` verildiyse arama sonuçlarını bu dokümanlarla sınırla.
  - `doc_ids` verilmediyse: tüm indeks (tüm dokümanlar) içinde ara.
- [ ] **Cevap üretimi**
  - Bağlama farklı dokümanlardan gelen chunk’lar birlikte girebilmeli.
  - Yanıtta kaynaklar doküman bazında görülebilmeli (en azından `doc_name` alanı ile).

**Kabul kriterleri (DoD)**
- Aynı soru farklı dokümanlarda kanıt gerektiriyorsa cevapta iki dokümandan da `sources` görünür.
- `doc_ids` ile sınırlandığında, sınır dışı dokümandan kaynak gelmez.

#### 5.4. Sprint 5 çıktıları (demo senaryosu)
- Kullanıcı 2 doküman yükler.
- `/summarize` ile:
  - `doc_id` verince tek doküman özeti alır.
  - `doc_ids` verince birleşik özet alır.
- `/chat` ile:
  - `doc_ids` boşken tüm dokümanlardan birleşik cevap alır.
  - `doc_ids` doluyken sadece seçili dokümanlardan cevap alır.

---

### Sprint 6: React UI
**Hedef:** Ödevin “minimum UI yeterli” şartını karşılayan React arayüzünü sıfırdan kurup backend ile entegre etmek.

- [ ] **React proje kurulumu:**
  - Sayfalar / bileşenler:
    - Upload alanı (çoklu dosya)
    - Chat ekranı (mesaj akışı)
    - Kaynaklar (accordion/expand)
    - Özetleme paneli (tek/çoklu doküman seçimi)
  - **Kabul kriteri:** React app ayağa kalkar; boş state’lerde kullanıcıyı yönlendiren UI mesajları vardır.

- [ ] **Backend entegrasyonu:**
  - Upload: `POST /upload` (çoklu dosya)
  - Chat: `POST /chat`
  - Summarize: `POST /summarize`
  - **Kabul kriteri:** Kullanıcı 2 dosya yükleyip chat’te soru sorar; cevap + kaynaklar UI’da görünür; özet butonu çalışır.

---
