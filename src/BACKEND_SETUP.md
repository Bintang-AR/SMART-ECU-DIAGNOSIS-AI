# 🚀 Setup Backend FastAPI

Panduan lengkap untuk setup backend FastAPI untuk aplikasi diagnostik mesin.

## 📋 Prerequisites

- Python 3.8 atau lebih baru
- pip (Python package manager)
- Model ML yang sudah ditraining (TensorFlow/PyTorch/Scikit-learn)

## 🛠️ Step-by-Step Setup

### 1. Buat Folder Backend

```bash
# Buat folder untuk backend
mkdir machine-diagnostics-backend
cd machine-diagnostics-backend
```

### 2. Setup Virtual Environment (Recommended)

```bash
# Buat virtual environment
python -m venv venv

# Activate virtual environment

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Copy file requirements.txt dari project ini
# Kemudian install:
pip install -r requirements.txt

# Atau install manual:
pip install fastapi uvicorn python-multipart librosa numpy scikit-learn
```

### 4. Copy File Backend

Copy file-file berikut dari project ini ke folder backend Anda:

```bash
# File utama
- backend_example.py  → rename menjadi main.py
- ml_model_example.py → untuk referensi integrasi model

# File pendukung
- requirements.txt
```

### 5. Siapkan Model ML

```bash
# Buat folder models
mkdir models

# Copy model Anda ke folder ini
# Contoh:
models/
  ├── tensorflow_model.h5    # Jika pakai TensorFlow
  ├── pytorch_model.pt        # Jika pakai PyTorch
  └── sklearn_model.pkl       # Jika pakai Scikit-learn
```

### 6. Konfigurasi Model di main.py

Edit `main.py` dan uncomment bagian model yang Anda gunakan:

```python
# Di bagian analyze_audio_data(), uncomment sesuai model:

# TensorFlow/Keras
from ml_model_example import TensorFlowModelHandler
model_handler = TensorFlowModelHandler("models/tensorflow_model.h5")

# PyTorch
# from ml_model_example import PyTorchModelHandler
# model_handler = PyTorchModelHandler("models/pytorch_model.pt")

# Scikit-learn
# from ml_model_example import ScikitLearnModelHandler
# model_handler = ScikitLearnModelHandler("models/sklearn_model.pkl")
```

### 7. Test Backend

```bash
# Jalankan server
python main.py

# Atau gunakan uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di: `http://localhost:8000`

### 8. Test API Endpoints

Buka browser dan akses:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

Atau test dengan cURL:

```bash
# Health check
curl http://localhost:8000/api/health

# Analyze audio (ganti dengan file audio Anda)
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_audio.webm" \
  -F "mode=quick"
```

## 🔧 Konfigurasi Frontend

Setelah backend berjalan, update URL di frontend:

Edit file `/services/api.ts` baris 18:

```typescript
// Local development
const API_BASE_URL = 'http://localhost:8000';

// Production (setelah deploy)
const API_BASE_URL = 'https://your-api-domain.com';
```

## 📂 Struktur Folder Backend

```
machine-diagnostics-backend/
├── main.py                 # File utama FastAPI
├── ml_model_example.py     # Helper untuk ML models
├── requirements.txt        # Dependencies
├── models/                 # Folder untuk model files
│   ├── tensorflow_model.h5
│   └── ...
├── logs/                   # Folder untuk logs (optional)
├── uploads/                # Folder temporary untuk uploads (optional)
└── .env                    # Environment variables (optional)
```

## 🌐 Deploy ke Production

### Option 1: Railway

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login dan deploy:
```bash
railway login
railway init
railway up
```

3. Set environment variables di Railway dashboard

### Option 2: Heroku

1. Install Heroku CLI

2. Buat `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

3. Deploy:
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Option 3: DigitalOcean App Platform

1. Connect GitHub repo
2. Configure build & run commands:
   - Build: `pip install -r requirements.txt`
   - Run: `uvicorn main:app --host 0.0.0.0 --port 8080`
3. Deploy

### Option 4: AWS EC2

1. Launch EC2 instance (Ubuntu)
2. SSH ke instance
3. Install Python & dependencies
4. Setup systemd service:

```bash
# /etc/systemd/system/fastapi.service
[Unit]
Description=FastAPI Machine Diagnostics
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/backend
Environment="PATH=/home/ubuntu/backend/venv/bin"
ExecStart=/home/ubuntu/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

5. Start service:
```bash
sudo systemctl start fastapi
sudo systemctl enable fastapi
```

### Option 5: Google Cloud Run

1. Buat `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

2. Build & deploy:
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/machine-diagnostics
gcloud run deploy --image gcr.io/PROJECT-ID/machine-diagnostics --platform managed
```

## 🔐 Environment Variables

Buat file `.env` untuk konfigurasi:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Model Configuration
MODEL_PATH=models/tensorflow_model.h5
MODEL_TYPE=tensorflow  # tensorflow, pytorch, sklearn

# CORS
ALLOWED_ORIGINS=https://your-frontend-domain.com,http://localhost:3000

# Database (optional)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Rate Limiting
RATE_LIMIT=100/hour
```

Load di main.py:

```python
from dotenv import load_dotenv
import os

load_dotenv()

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
MODEL_PATH = os.getenv("MODEL_PATH", "models/model.h5")
```

## 📊 Monitoring & Logging

### Setup Logging

```python
import logging
from logging.handlers import RotatingFileHandler

# Setup logger
logger = logging.getLogger("machine_diagnostics")
logger.setLevel(logging.INFO)

# File handler
handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10485760,  # 10MB
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Metrics dengan Prometheus

```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
```

Access metrics: http://localhost:8000/metrics

## 🐛 Troubleshooting

### Error: Port already in use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Error: Module not found

```bash
# Pastikan virtual environment active
# Reinstall dependencies
pip install -r requirements.txt
```

### Error: Model file not found

```bash
# Check path model
ls models/

# Update path di code
MODEL_PATH = "models/your_model.h5"
```

### Error: CORS issues

Tambahkan domain frontend ke CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend-domain.com"
    ],
    ...
)
```

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Librosa Documentation](https://librosa.org/)
- [TensorFlow Guide](https://www.tensorflow.org/guide)
- [PyTorch Guide](https://pytorch.org/tutorials/)

## 💬 Support

Jika ada masalah:
1. Check logs di terminal
2. Periksa API docs di /docs
3. Test endpoint dengan cURL
4. Verify model file exists
5. Check CORS configuration

## ✅ Checklist

Sebelum production:
- [ ] Model ML sudah terintegrasi
- [ ] API endpoints tested
- [ ] CORS configured dengan domain spesifik
- [ ] Environment variables setup
- [ ] Logging configured
- [ ] Error handling implemented
- [ ] Rate limiting enabled
- [ ] HTTPS enabled
- [ ] Monitoring setup
- [ ] Backup strategy defined
