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

**4. Backend'i Başlatın (FastAPI):**

```bash
uvicorn backend.main:app --reload --port 8000
```

**4. Frontend'i Başlatın (React UI):**

```bash
cd frontend
npm install
npm run dev
```

API çalışmaya başladığında aşağıdaki adreslere erişebilirsiniz:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **Upload Endpoint:** `POST http://127.0.0.1:8000/upload`

**5. Vektör Aramasını Test Etme (FAISS):**

Sisteme yüklediğiniz belgeler üzerinde semantic arama yapmak için terminalde `test_search.py` betiğini kullanabilirsiniz:

```bash
# Sanal ortam aktifken çalıştırın:
python test_search.py "Aramak istediğiniz metin veya soru" --k 5
```
*(Not: `--k 5` parametresi en yakın 5 sonucu getirir. Varsayılan değer 3'tür.)*
