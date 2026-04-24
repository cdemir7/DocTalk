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

**4. .env Dosyasını Ayarlayın:**

Projeyi çalıştırmadan önce Google Gemini API anahtarına ihtiyacınız var:
1. [Google AI Studio](https://aistudio.google.com/) adresine gidin.
2. Hesabınıza giriş yapın ve yeni bir "API key" oluşturun.
3. Proje dizininde bulunan `.env.example` dosyasını kopyalayarak yeni bir `.env` dosyası oluşturun.
4. Oluşturduğunuz `.env` dosyasını açın ve `GEMINI_API_KEY` değerine aldığınız API anahtarını yapıştırın:
   ```env
   GEMINI_API_KEY="sizin_api_anahtariniz_buraya"
   ```

**5. Backend'i Başlatın (FastAPI):**

```bash
uvicorn backend.main:app --reload --port 8000
```

**6. Frontend'i Başlatın (React UI):**

```bash
cd frontend
npm install
npm run dev
```

API çalışmaya başladığında aşağıdaki adreslere erişebilirsiniz:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **Upload Endpoint:** `POST http://127.0.0.1:8000/upload`

**7. Vektör Aramasını Test Etme (FAISS):**

Sisteme yüklediğiniz belgeler üzerinde semantic arama yapmak için terminalde `test_search.py` betiğini kullanabilirsiniz:

```bash
# Sanal ortam aktifken çalıştırın:
python test_search.py "Aramak istediğiniz metin veya soru" --k 5
```
*(Not: `--k 5` parametresi en yakın 5 sonucu getirir. Varsayılan değer 3'tür.)*
