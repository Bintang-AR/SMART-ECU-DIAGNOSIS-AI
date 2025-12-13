# 🔧 Aplikasi Diagnostik Mesin dengan AI

Aplikasi diagnostik mesin berbasis web yang menggunakan teknologi audio analysis dan machine learning untuk mendeteksi masalah pada mesin industri.

## 🎯 Fitur Utama

- ✅ **Scan Mesin** - Rekam suara mesin dengan microphone
- ✅ **Quick & Deep Scan** - Pilihan mode pemindaian cepat (5s) atau mendalam (15s)
- ✅ **Analisis AI** - Deteksi masalah dengan machine learning
- ✅ **Hasil Diagnosis** - Tampilan health score dan daftar masalah terdeteksi
- ✅ **Spectrogram Viewer** - Visualisasi interaktif data getaran dengan zoom & timeline
- ✅ **Mode Offline** - Simpan rekaman lokal untuk diproses saat online
- ✅ **Integrasi FastAPI** - Backend Python dengan model ML Anda

## 🏗️ Arsitektur

```
Frontend (React + TypeScript)
         ↕
    HTTP/HTTPS
         ↕
Backend (FastAPI + Python)
         ↕
   ML Model (TensorFlow/PyTorch)
```

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS untuk styling
- Recharts untuk visualisasi
- MediaRecorder API untuk audio recording

**Backend:**
- FastAPI (Python)
- Librosa untuk audio processing
- TensorFlow/PyTorch/Scikit-learn untuk ML model
- CORS enabled untuk komunikasi dengan frontend

## 📚 Dokumentasi

### Quick Start

1. **Frontend** - Aplikasi sudah ready, tinggal konfigurasi API URL
2. **Backend** - Setup FastAPI dan integrasi model ML

### Dokumentasi Detail

- 📘 **[BACKEND_SETUP.md](BACKEND_SETUP.md)** - Panduan setup backend FastAPI
- 📗 **[FASTAPI_INTEGRATION.md](FASTAPI_INTEGRATION.md)** - Detail integrasi API
- 📙 **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arsitektur & flow diagram lengkap
- 📓 **[backend_example.py](backend_example.py)** - Template backend siap pakai
- 📕 **[ml_model_example.py](ml_model_example.py)** - Contoh integrasi model ML

## 🚀 Quick Setup

### Frontend (Sudah Ready!)

Aplikasi frontend sudah siap digunakan. Tinggal konfigurasi URL backend:

Edit `/services/api.ts` baris 18:

```typescript
const API_BASE_URL = 'http://localhost:8000';  // Ganti dengan URL backend Anda
```

### Backend Setup

1. **Buat folder backend:**
```bash
mkdir machine-diagnostics-backend
cd machine-diagnostics-backend
```

2. **Copy file backend_example.py:**
```bash
# Copy dan rename ke main.py
cp backend_example.py main.py
```

3. **Install dependencies:**
```bash
pip install fastapi uvicorn python-multipart librosa numpy scikit-learn
```

4. **Siapkan model ML:**
```bash
mkdir models
# Copy model Anda (.h5, .pt, .pkl) ke folder models/
```

5. **Jalankan backend:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Test:**
- Open: http://localhost:8000/docs
- Test health: http://localhost:8000/api/health

**Selesai!** Frontend akan otomatis terhubung dengan backend.

## 🔧 Konfigurasi

### Frontend Configuration

File: `/services/api.ts`

```typescript
// Development
const API_BASE_URL = 'http://localhost:8000';

// Production
const API_BASE_URL = 'https://api.yourdomain.com';
```

### Backend Configuration

File: `main.py`

```python
# Load model Anda
from ml_model_example import TensorFlowModelHandler
model_handler = TensorFlowModelHandler("models/your_model.h5")

# Gunakan di endpoint analyze
result = model_handler.predict(audio_bytes, mode)
```

## 📊 API Endpoints

### GET `/api/health`
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2025-12-13T10:00:00"
}
```

### POST `/api/analyze`
Analisis audio mesin

**Request:**
- `file`: Audio file (multipart/form-data)
- `mode`: "quick" atau "deep"

**Response:**
```json
{
  "overall_health": 75,
  "issues": [
    {
      "severity": "medium",
      "component": "Bearing Motor",
      "description": "Terdeteksi getaran abnormal",
      "recommendation": "Lakukan inspeksi dalam 7 hari"
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

### GET `/api/history`
Get riwayat analisis (optional, perlu database)

## 🧠 Integrasi Model ML

### TensorFlow/Keras

```python
from ml_model_example import TensorFlowModelHandler

model = TensorFlowModelHandler("models/model.h5")
result = model.predict(audio_bytes, mode="quick")
```

### PyTorch

```python
from ml_model_example import PyTorchModelHandler

model = PyTorchModelHandler("models/model.pt")
result = model.predict(audio_bytes, mode="deep")
```

### Scikit-learn

```python
from ml_model_example import ScikitLearnModelHandler

model = ScikitLearnModelHandler("models/model.pkl")
result = model.predict(audio_bytes, mode="quick")
```

## 🎨 Skema Warna

- **Background**: Black (#000000)
- **Cards**: Gray-800 (#1F2937)
- **Primary Button**: Red-600 to Red-700 gradient
- **Text**: White & Gray variations
- **Accents**: Red-500 (#EF4444)

## 📱 Fitur Mode Offline

1. User toggle mode offline
2. Rekaman disimpan di localStorage
3. Tampilkan mock data untuk preview
4. Saat online, otomatis kirim semua rekaman ke server
5. Hapus dari localStorage setelah berhasil diproses

## 🔒 Security Checklist

Frontend:
- ✅ HTTPS only (production)
- ✅ Input validation
- ✅ Secure localStorage

Backend:
- ✅ CORS configuration
- ✅ File size limits (50MB max)
- ✅ Rate limiting
- ✅ Error handling
- ✅ Input sanitization

## 🚀 Deployment

### Frontend
- **Vercel** (recommended)
- **Netlify**
- **AWS S3 + CloudFront**
- **Firebase Hosting**

### Backend
- **Railway** (recommended untuk Python)
- **Heroku**
- **DigitalOcean App Platform**
- **AWS EC2**
- **Google Cloud Run**

## 🧪 Testing

### Test Frontend
1. Klik tombol "Scan Mesin"
2. Izinkan akses microphone
3. Recording akan berjalan 5s (quick) atau 15s (deep)
4. Lihat hasil diagnosis

### Test Backend
```bash
# Health check
curl http://localhost:8000/api/health

# Analyze audio
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_audio.webm" \
  -F "mode=quick"
```

## 📁 Struktur Project

```
/
├── App.tsx                    # Main component
├── services/
│   └── api.ts                # API service untuk FastAPI
├── components/
│   ├── MainScan.tsx          # Scan UI & recording
│   ├── DiagnosisResults.tsx  # Display results
│   └── SpectrogramViewer.tsx # Visualization
├── BACKEND_SETUP.md          # Panduan setup backend
├── FASTAPI_INTEGRATION.md    # Detail integrasi
├── ARCHITECTURE.md           # Arsitektur lengkap
├── backend_example.py        # Template backend
├── ml_model_example.py       # Contoh integrasi ML
└── requirements.txt          # Python dependencies
```

## 🛠️ Tech Stack

### Frontend
- React 18
- TypeScript
- Tailwind CSS v4
- Recharts
- Lucide React (icons)
- MediaRecorder API

### Backend (Setup Required)
- FastAPI
- Python 3.8+
- Librosa (audio processing)
- NumPy
- TensorFlow / PyTorch / Scikit-learn

## 💡 Tips

1. **Model Performance**: Gunakan quantized model untuk inference lebih cepat
2. **Caching**: Implement Redis untuk cache hasil yang sama
3. **Background Tasks**: Gunakan Celery untuk processing yang lama
4. **Monitoring**: Setup Sentry untuk error tracking
5. **Database**: Gunakan PostgreSQL/MongoDB untuk simpan history

## 🐛 Troubleshooting

### Frontend tidak bisa connect ke backend
- Periksa `API_BASE_URL` di `/services/api.ts`
- Pastikan backend running di port 8000
- Check CORS configuration di backend

### Microphone access denied
- Pastikan browser mendapat izin
- HTTPS required untuk production
- localhost OK untuk development

### Model inference lambat
- Gunakan GPU jika tersedia
- Optimize model (pruning, quantization)
- Implement model caching

## 📞 Support

Jika ada pertanyaan atau masalah:

1. Baca dokumentasi lengkap di:
   - BACKEND_SETUP.md
   - FASTAPI_INTEGRATION.md
   - ARCHITECTURE.md

2. Check example files:
   - backend_example.py
   - ml_model_example.py

3. Review logs di terminal

## 📝 License

Aplikasi ini untuk keperluan pembelajaran dan development.

## 🎯 Roadmap

- [x] Frontend React dengan recording
- [x] API service untuk FastAPI
- [x] Mode offline dengan localStorage
- [x] Spectrogram visualization
- [ ] User authentication
- [ ] Database integration
- [ ] Historical data analysis
- [ ] Real-time monitoring
- [ ] Mobile app version

## ⭐ Features Highlight

### 🎤 Audio Recording
- Real-time microphone access
- Configurable duration (5s / 15s)
- Progress indicator
- Auto-stop when complete

### 🤖 AI Analysis
- Multiple ML framework support
- Feature extraction dengan librosa
- Real-time inference
- Confidence scoring

### 📊 Data Visualization
- Interactive spectrogram
- Zoom & pan controls
- Timeline navigation
- Frequency analysis

### 💾 Offline Support
- Local storage for recordings
- Auto-sync when online
- Background processing
- No data loss

---

**Ready to integrate with your ML model!** 🚀

Mulai dengan membaca [BACKEND_SETUP.md](BACKEND_SETUP.md) untuk setup backend FastAPI.
