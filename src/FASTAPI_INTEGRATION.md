# Panduan Integrasi FastAPI Backend

Dokumen ini menjelaskan cara mengintegrasikan frontend React dengan backend FastAPI untuk aplikasi diagnostik mesin.

## 📋 Persiapan Backend

### 1. Install Dependencies

```bash
pip install fastapi uvicorn python-multipart librosa numpy tensorflow
```

### 2. Contoh Implementasi Backend (main.py)

```python
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import numpy as np
import librosa
from typing import List, Dict, Any

app = FastAPI(title="Machine Diagnostics API")

# CORS Configuration - PENTING untuk integrasi dengan frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk production: ganti dengan domain spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model ML Anda (contoh)
# model = load_your_model('path/to/model.h5')

@app.get("/api/health")
async def health_check():
    """Endpoint untuk cek kesehatan server"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    mode: str = Form(...)
):
    """
    Endpoint utama untuk analisis audio mesin
    
    Parameters:
    - file: File audio (webm/wav format)
    - mode: 'quick' atau 'deep'
    
    Returns:
    - overall_health: Score kesehatan mesin (0-100)
    - issues: List masalah yang terdeteksi
    - vibration_data: Data getaran untuk visualisasi
    """
    
    try:
        # Baca file audio
        audio_bytes = await file.read()
        
        # STEP 1: Preprocessing Audio
        # Convert audio ke format yang bisa diproses
        # Contoh menggunakan librosa:
        # audio_data, sr = librosa.load(io.BytesIO(audio_bytes), sr=44100)
        
        # STEP 2: Feature Extraction
        # Extract fitur dari audio (MFCC, Mel-spectrogram, dll)
        # features = extract_features(audio_data, sr)
        
        # STEP 3: Model Inference
        # Jalankan model ML untuk prediksi
        # prediction = model.predict(features)
        
        # CONTOH RESPONSE (ganti dengan hasil model Anda):
        result = {
            "overall_health": 75,  # Score dari model
            "issues": [
                {
                    "severity": "medium",
                    "component": "Bearing Motor",
                    "description": "Terdeteksi getaran abnormal pada frekuensi 120 Hz",
                    "recommendation": "Lakukan inspeksi visual dalam 7 hari"
                }
            ],
            "vibration_data": [
                {
                    "time": i * 0.01,
                    "amplitude": float(np.sin(i * 0.1) * 2),
                    "frequency": float(60 + np.sin(i * 0.05) * 60)
                }
                for i in range(100)
            ]
        }
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "overall_health": 0,
            "issues": [],
            "vibration_data": []
        }

@app.get("/api/history")
async def get_history(limit: int = 10):
    """
    Endpoint untuk mengambil riwayat analisis
    (Optional - jika Anda menyimpan data ke database)
    """
    # Query dari database
    # records = db.query(DiagnosisRecord).limit(limit).all()
    
    return {
        "records": []  # Return data dari database
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 🚀 Menjalankan Backend

### Development (Local)

```bash
# Jalankan dengan auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server akan berjalan di: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Production

```bash
# Gunakan gunicorn untuk production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔧 Konfigurasi Frontend

Edit file `/services/api.ts` baris 18:

```typescript
// Development (local)
const API_BASE_URL = 'http://localhost:8000';

// Production (ganti dengan URL server Anda)
const API_BASE_URL = 'https://api.yourserver.com';
```

## 📊 Format Data API

### Request (POST /api/analyze)

```
Content-Type: multipart/form-data

file: [Audio File Binary]
mode: "quick" | "deep"
```

### Response

```json
{
  "overall_health": 75,
  "issues": [
    {
      "severity": "low" | "medium" | "high",
      "component": "Bearing Motor",
      "description": "Deskripsi masalah",
      "recommendation": "Rekomendasi tindakan"
    }
  ],
  "vibration_data": [
    {
      "time": 0.01,
      "amplitude": 2.5,
      "frequency": 120
    }
  ]
}
```

## 🧠 Integrasi Model Machine Learning

### Contoh untuk TensorFlow/Keras

```python
import tensorflow as tf

# Load model
model = tf.keras.models.load_model('model.h5')

# Preprocessing
def preprocess_audio(audio_data, sr):
    # Extract MFCC features
    mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=40)
    mfccs_scaled = np.mean(mfccs.T, axis=0)
    return mfccs_scaled.reshape(1, -1)

# Prediction
features = preprocess_audio(audio_data, sr)
prediction = model.predict(features)
health_score = float(prediction[0][0] * 100)
```

### Contoh untuk PyTorch

```python
import torch
import torch.nn as nn

# Load model
model = torch.load('model.pt')
model.eval()

# Prediction
with torch.no_grad():
    features_tensor = torch.from_numpy(features).float()
    prediction = model(features_tensor)
    health_score = float(prediction.item() * 100)
```

## 🔒 Security (Production)

### 1. Gunakan HTTPS

```python
# Setup dengan SSL certificate
uvicorn.run(
    app,
    host="0.0.0.0",
    port=443,
    ssl_keyfile="path/to/key.pem",
    ssl_certfile="path/to/cert.pem"
)
```

### 2. Batasi CORS Origins

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.com",
        "https://www.yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/analyze")
@limiter.limit("10/minute")
async def analyze_audio(...):
    ...
```

## 📱 Testing API

### Menggunakan cURL

```bash
# Test health check
curl http://localhost:8000/api/health

# Test analyze (dengan file audio)
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@recording.webm" \
  -F "mode=quick"
```

### Menggunakan Python requests

```python
import requests

# Upload file
with open('recording.webm', 'rb') as f:
    files = {'file': f}
    data = {'mode': 'quick'}
    response = requests.post(
        'http://localhost:8000/api/analyze',
        files=files,
        data=data
    )
    print(response.json())
```

## 🐛 Troubleshooting

### Error: CORS Policy

**Solusi:** Pastikan CORS middleware sudah dikonfigurasi di FastAPI

### Error: Connection Refused

**Solusi:** 
- Periksa apakah FastAPI server berjalan
- Periksa URL di `/services/api.ts` sudah benar
- Periksa firewall tidak memblokir port 8000

### Error: Microphone Access Denied

**Solusi:**
- Pastikan browser mendapat izin akses microphone
- Gunakan HTTPS untuk production (microphone hanya bekerja di HTTPS/localhost)

### Error: File Upload Too Large

**Solusi:** Tambahkan konfigurasi di FastAPI:

```python
from fastapi import FastAPI

app = FastAPI()
app.add_middleware(
    middleware_class=...,
    max_upload_size=50 * 1024 * 1024  # 50MB
)
```

## 📚 Resources

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Librosa Documentation: https://librosa.org/doc/
- TensorFlow Audio Processing: https://www.tensorflow.org/io/tutorials/audio
- Web Audio API: https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API

## 💡 Tips

1. **Gunakan async/await** untuk handling file upload yang besar
2. **Implementasi caching** untuk request yang sama
3. **Logging** semua request untuk debugging
4. **Validasi input** untuk mencegah error
5. **Monitoring** performa model (inference time, accuracy)
6. **Background tasks** untuk processing yang lama

```python
from fastapi import BackgroundTasks

@app.post("/api/analyze")
async def analyze_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    mode: str = Form(...)
):
    # Process immediately
    result = quick_analysis(file)
    
    # Process in background
    background_tasks.add_task(deep_analysis, file, mode)
    
    return result
```
