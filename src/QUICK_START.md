# ⚡ Quick Start Guide

Panduan cepat untuk mulai menggunakan aplikasi diagnostik mesin dengan FastAPI backend.

## 🎯 Ringkasan

Frontend sudah ready ✅  
Backend perlu setup ⚙️

## 📦 Yang Anda Butuhkan

1. ✅ **Frontend**: Aplikasi React ini (sudah selesai)
2. 📦 **Backend**: FastAPI server (perlu setup)
3. 🧠 **Model ML**: Model yang sudah ditraining (TensorFlow/PyTorch/Scikit-learn)

## 🚀 Setup dalam 5 Menit

### Step 1: Setup Backend (3 menit)

```bash
# 1. Buat folder backend
mkdir backend && cd backend

# 2. Install dependencies
pip install fastapi uvicorn python-multipart librosa numpy

# 3. Copy file template (dari project ini)
# Copy: backend_example.py → main.py

# 4. Jalankan server
uvicorn main:app --reload --port 8000
```

✅ Backend running di: http://localhost:8000

### Step 2: Konfigurasi Frontend (30 detik)

Edit file `/services/api.ts` baris 18:

```typescript
const API_BASE_URL = 'http://localhost:8000';
```

✅ Frontend siap terhubung dengan backend!

### Step 3: Test Aplikasi (1 menit)

1. Buka aplikasi di browser
2. Klik tombol **"Scan Mesin"**
3. Izinkan akses microphone
4. Tunggu recording selesai
5. Lihat hasil diagnosis!

---

## 📋 Checklist

Sebelum mulai, pastikan:

- [ ] Python 3.8+ terinstall
- [ ] Node.js & npm terinstall (untuk frontend)
- [ ] Microphone tersedia
- [ ] Browser support MediaRecorder API (Chrome/Firefox/Edge)

## 🔧 Struktur File

```
Project ini:
├── /services/api.ts          ← API service (sudah ready)
├── /components/               ← React components (sudah ready)
├── backend_example.py         ← Copy ini ke backend/main.py
├── ml_model_example.py        ← Referensi integrasi model
└── requirements.txt           ← Python dependencies

Backend Anda (buat baru):
backend/
├── main.py                    ← Copy dari backend_example.py
├── ml_model_example.py        ← Copy untuk referensi
├── models/                    ← Folder untuk model ML
│   └── your_model.h5/.pt/.pkl
└── requirements.txt           ← Copy dari project
```

## 🧪 Test Backend

```bash
# 1. Test health check
curl http://localhost:8000/api/health

# 2. Test dengan Python script
python test_api.py

# 3. Open API docs
# Browser: http://localhost:8000/docs
```

## 🧠 Integrasi Model ML (5 menit)

Edit `backend/main.py`, uncomment bagian ini:

### Untuk TensorFlow:

```python
# Import
from ml_model_example import TensorFlowModelHandler

# Di startup
model_handler = TensorFlowModelHandler("models/your_model.h5")

# Di endpoint analyze
result = model_handler.predict(audio_bytes, mode)
```

### Untuk PyTorch:

```python
# Import
from ml_model_example import PyTorchModelHandler

# Di startup
model_handler = PyTorchModelHandler("models/your_model.pt")

# Di endpoint analyze
result = model_handler.predict(audio_bytes, mode)
```

### Untuk Scikit-learn:

```python
# Import
from ml_model_example import ScikitLearnModelHandler

# Di startup
model_handler = ScikitLearnModelHandler("models/your_model.pkl")

# Di endpoint analyze
result = model_handler.predict(audio_bytes, mode)
```

## 🎨 Tampilan Aplikasi

### 1. Halaman Scan
- Toggle online/offline mode
- Pilih Quick (5s) atau Deep (15s) scan
- Tombol besar "Scan Mesin"
- Progress bar saat recording

### 2. Halaman Hasil
- Health score (0-100)
- List issues dengan severity
- Recommendations
- Button "Lihat Spectrogram"

### 3. Spectrogram Viewer
- Interactive timeline
- Zoom in/out
- Amplitude & frequency chart
- Back button

## 🌐 Mode Offline

**Cara kerja:**
1. User toggle offline mode (ikon wifi)
2. Recording tetap jalan dan disimpan di localStorage
3. Tampilkan mock data untuk preview
4. Saat toggle online, semua rekaman otomatis dikirim ke server

**Implementasi:**
- Sudah terintegrasi di `MainScan.tsx`
- Menggunakan localStorage browser
- Auto-sync saat kembali online

## 🔥 Tips Cepat

### Development
```bash
# Backend
uvicorn main:app --reload --port 8000

# Frontend (jika pakai local dev server)
npm run dev
```

### Debug
```bash
# Check backend logs
# Terminal akan show semua request

# Check frontend console
# Browser DevTools → Console
```

### Common Issues

**Backend tidak connect:**
```bash
# Periksa URL di /services/api.ts
# Pastikan backend running
# Check CORS enabled di FastAPI
```

**Microphone tidak berfungsi:**
```bash
# Chrome: Settings → Privacy → Microphone
# Pastikan site mendapat permission
# HTTPS required untuk production (localhost OK)
```

**Model error:**
```bash
# Check model file exists: ls backend/models/
# Check path di main.py
# Verify dependencies installed
```

## 📚 Dokumentasi Lengkap

Untuk detail lebih lanjut:

1. **[BACKEND_SETUP.md](BACKEND_SETUP.md)** - Setup backend lengkap
2. **[FASTAPI_INTEGRATION.md](FASTAPI_INTEGRATION.md)** - Detail API
3. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Arsitektur sistem
4. **[README.md](README.md)** - Overview lengkap

## 💡 Next Steps

Setelah aplikasi berjalan:

1. ✅ Train model ML yang lebih baik
2. ✅ Improve preprocessing audio
3. ✅ Add database untuk history
4. ✅ Deploy ke production
5. ✅ Add authentication (optional)
6. ✅ Setup monitoring

## 🎯 Production Deployment

### Frontend
Pilih salah satu:
- **Vercel** (recommended)
- **Netlify**
- **AWS S3 + CloudFront**

### Backend
Pilih salah satu:
- **Railway** (recommended, easy Python deploy)
- **Heroku**
- **DigitalOcean**
- **AWS EC2**

### Update URLs
Setelah deploy, update `API_BASE_URL` di `/services/api.ts` dengan URL production.

## 📞 Need Help?

1. Check logs di terminal (backend)
2. Check browser console (frontend)
3. Review dokumentasi:
   - BACKEND_SETUP.md
   - FASTAPI_INTEGRATION.md
4. Test dengan: `python test_api.py`

## ⚡ Quick Commands

```bash
# Backend
cd backend
python main.py                          # Start server
python test_api.py                      # Test API
curl localhost:8000/api/health         # Health check

# Check logs
tail -f logs/app.log                   # If logging enabled

# Install dependencies
pip install -r requirements.txt
pip list | grep fastapi                # Verify install
```

## 🎉 You're Ready!

Sekarang Anda punya:
- ✅ Frontend React yang lengkap
- ✅ Backend FastAPI template
- ✅ API integration yang siap pakai
- ✅ Mode offline support
- ✅ Dokumentasi lengkap

**Tinggal:**
1. Setup backend (3 menit)
2. Integrasikan model ML Anda (5 menit)
3. Test & deploy!

---

**Happy Coding!** 🚀

Jika ada pertanyaan, baca dokumentasi lengkap atau check example files yang sudah disediakan.
