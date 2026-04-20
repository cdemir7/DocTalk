# DocTalk

## Kurulum ve Çalıştırma

**1. Sanal Ortam Oluşturun:**
```bash
python3 -m venv ./.venv
```

**2. Sanal Ortamı Aktif Edin:**
- Mac / Linux:
```bash
source .venv/bin/activate
```
- Windows:
```bash
.venv\Scripts\activate
```

**3. Gerekli Paketleri Yükleyin:**
```bash
pip install -r requirements.txt
```

**4. Groq API Anahtarını Ayarlayın:**

`.env example` dosyasını kopyalayarak `.env` dosyası oluşturun ve anahtarınızı girin:
```bash
cp ".env example" .env
```
Ardından `.env` dosyasını açıp `GROQ_API_KEY` değerini doldurun:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

> **Not:** API anahtarınızı `.env` dosyasına eklemek zorunda değilsiniz.  
> Uygulamayı başlattıktan sonra **Streamlit arayüzündeki yan panelden** (sidebar) de girebilirsiniz.  
> Groq API anahtarı almak için → https://console.groq.com

**5. Backend'i Başlatın (FastAPI):**

```bash
uvicorn backend.main:app --reload --port 8000
```

API çalışmaya başladığında aşağıdaki adreslere erişebilirsiniz:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **Upload Endpoint:** `POST http://127.0.0.1:8000/upload`

**6. Frontend'i Başlatın (Streamlit):**
```bash
streamlit run frontend/app.py
```