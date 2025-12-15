# Panduan Integrasi Model .h5 dengan Backend FastAPI

## 📋 Daftar Isi
1. [Persiapan](#persiapan)
2. [Struktur File Backend](#struktur-file-backend)
3. [Implementasi Integrasi](#implementasi-integrasi)
4. [Testing](#testing)
5. [Troubleshooting](#troubleshooting)

---

## 🚀 Persiapan

### 1. Install Dependencies Python

Buat file `requirements.txt` untuk backend Anda:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
tensorflow==2.15.0
librosa==0.10.1
numpy==1.24.3
python-dotenv==1.0.0
```

Install semua dependencies:
```bash
pip install -r requirements.txt
```

### 2. Struktur Folder Backend

Buat struktur folder seperti ini:

```
backend/
├── main.py                 # File utama FastAPI
├── model_handler.py        # Handler untuk load dan predict model
├── requirements.txt        # Dependencies
├── models/                 # Folder untuk menyimpan model
│   └── model.h5           # Model Anda (copy ke sini)
└── .env                    # Environment variables (opsional)
```

---

## 🔧 Implementasi Integrasi

### Step 1: Buat Model Handler

Buat file `model_handler.py` untuk mengelola model Anda:

```python
import tensorflow as tf
import numpy as np
import librosa
import io
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class MachineModelHandler:
    """Handler untuk model diagnostik mesin (.h5)"""
    
    def __init__(self, model_path: str):
        """
        Inisialisasi dan load model
        
        Args:
            model_path: Path ke file model.h5
        """
        try:
            # Load model Keras/TensorFlow
            self.model = tf.keras.models.load_model(model_path)
            logger.info(f"✅ Model berhasil dimuat dari: {model_path}")
            logger.info(f"Input shape: {self.model.input_shape}")
            logger.info(f"Output shape: {self.model.output_shape}")
            
        except Exception as e:
            logger.error(f"❌ Gagal memuat model: {e}")
            raise
    
    def preprocess_audio(self, audio_bytes: bytes, mode: str) -> np.ndarray:
        """
        Preprocessing audio untuk model
        
        PENTING: Sesuaikan preprocessing ini dengan cara Anda melatih model!
        
        Args:
            audio_bytes: Raw audio data dari frontend
            mode: 'quick' (5s) atau 'deep' (15s)
            
        Returns:
            Features array siap untuk model
        """
        # Load audio dari bytes
        audio_data, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=44100,  # Sample rate (sesuaikan dengan training)
            mono=True
        )
        
        # ===== CONTOH FEATURE EXTRACTION =====
        # Sesuaikan dengan preprocessing yang Anda gunakan saat training!
        
        # 1. MFCC (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(
            y=audio_data,
            sr=sr,
            n_mfcc=40,      # Jumlah MFCC coefficients
            n_fft=2048,     # FFT window size
            hop_length=512  # Hop length
        )
        
        # 2. Statistik MFCC (mean dan std)
        mfccs_mean = np.mean(mfccs, axis=1)
        mfccs_std = np.std(mfccs, axis=1)
        
        # 3. Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)
        
        # 4. Zero Crossing Rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)
        
        # 5. Chroma features (opsional)
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        
        # 6. Spectral Contrast (opsional)
        contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
        contrast_mean = np.mean(contrast, axis=1)
        
        # Gabungkan semua features
        features = np.concatenate([
            mfccs_mean,                      # 40 features
            mfccs_std,                       # 40 features
            [np.mean(spectral_centroid)],    # 1 feature
            [np.std(spectral_centroid)],     # 1 feature
            [np.mean(spectral_rolloff)],     # 1 feature
            [np.mean(spectral_bandwidth)],   # 1 feature
            [np.mean(zcr)],                  # 1 feature
            chroma_mean,                     # 12 features
            contrast_mean                    # 7 features
        ])
        
        # Reshape untuk input model: (1, num_features)
        # Jika model Anda butuh shape berbeda, sesuaikan di sini!
        return features.reshape(1, -1)
    
    def interpret_prediction(self, prediction: np.ndarray, mode: str) -> Dict[str, Any]:
        """
        Interpretasi hasil prediksi model menjadi format untuk frontend
        
        PENTING: Sesuaikan dengan output model Anda!
        
        Args:
            prediction: Output dari model.predict()
            mode: 'quick' atau 'deep'
            
        Returns:
            Dictionary berisi overall_health dan issues
        """
        
        # ===== CONTOH 1: Model dengan output multi-class =====
        # Asumsi output: [health_score, bearing_prob, belt_prob, mounting_prob]
        
        if len(prediction[0]) >= 4:
            health_score = float(prediction[0][0] * 100)  # Normalize ke 0-100
            bearing_prob = float(prediction[0][1])
            belt_prob = float(prediction[0][2])
            mounting_prob = float(prediction[0][3])
            
            issues = []
            
            # Bearing issues
            if bearing_prob > 0.7:
                issues.append({
                    "severity": "high",
                    "component": "Bearing Motor",
                    "description": f"Terdeteksi masalah serius pada bearing (confidence: {bearing_prob:.1%})",
                    "recommendation": "Segera lakukan penggantian bearing dalam 48 jam untuk mencegah kerusakan lebih lanjut"
                })
            elif bearing_prob > 0.4:
                issues.append({
                    "severity": "medium",
                    "component": "Bearing Motor",
                    "description": f"Kemungkinan masalah pada bearing (confidence: {bearing_prob:.1%})",
                    "recommendation": "Lakukan inspeksi bearing dalam 7 hari dan monitor getaran"
                })
            
            # Belt issues
            if belt_prob > 0.6:
                issues.append({
                    "severity": "high",
                    "component": "Belt Transmisi",
                    "description": f"Terdeteksi masalah pada belt (confidence: {belt_prob:.1%})",
                    "recommendation": "Ganti belt transmisi atau sesuaikan ketegangan dalam 3 hari"
                })
            elif belt_prob > 0.3:
                issues.append({
                    "severity": "medium",
                    "component": "Belt Transmisi",
                    "description": f"Ketegangan belt tidak optimal (confidence: {belt_prob:.1%})",
                    "recommendation": "Sesuaikan ketegangan belt pada maintenance berikutnya"
                })
            
            # Mounting issues
            if mounting_prob > 0.5:
                issues.append({
                    "severity": "medium",
                    "component": "Mounting Base",
                    "description": f"Getaran pada mounting base (confidence: {mounting_prob:.1%})",
                    "recommendation": "Periksa baut mounting dan kencangkan jika perlu"
                })
            elif mounting_prob > 0.3:
                issues.append({
                    "severity": "low",
                    "component": "Mounting Base",
                    "description": f"Sedikit getaran resonansi (confidence: {mounting_prob:.1%})",
                    "recommendation": "Monitor secara berkala, belum perlu tindakan segera"
                })
        
        # ===== CONTOH 2: Model binary classification =====
        # Asumsi output: [normal_prob, fault_prob]
        elif len(prediction[0]) == 2:
            normal_prob = float(prediction[0][0])
            fault_prob = float(prediction[0][1])
            
            health_score = normal_prob * 100
            
            issues = []
            if fault_prob > 0.7:
                issues.append({
                    "severity": "high",
                    "component": "Motor",
                    "description": f"Terdeteksi anomali pada mesin (confidence: {fault_prob:.1%})",
                    "recommendation": "Segera lakukan pemeriksaan menyeluruh"
                })
            elif fault_prob > 0.4:
                issues.append({
                    "severity": "medium",
                    "component": "Motor",
                    "description": f"Kemungkinan anomali (confidence: {fault_prob:.1%})",
                    "recommendation": "Lakukan inspeksi dalam waktu dekat"
                })
        
        # ===== CONTOH 3: Model single output (regression) =====
        else:
            health_score = float(prediction[0][0] * 100)
            
            issues = []
            if health_score < 50:
                issues.append({
                    "severity": "high",
                    "component": "Motor",
                    "description": "Kondisi mesin dalam keadaan buruk",
                    "recommendation": "Segera lakukan maintenance komprehensif"
                })
            elif health_score < 70:
                issues.append({
                    "severity": "medium",
                    "component": "Motor",
                    "description": "Kondisi mesin memerlukan perhatian",
                    "recommendation": "Jadwalkan maintenance dalam minggu ini"
                })
            elif health_score < 85:
                issues.append({
                    "severity": "low",
                    "component": "Motor",
                    "description": "Kondisi mesin masih baik dengan penurunan performa kecil",
                    "recommendation": "Monitor secara rutin"
                })
        
        # Pastikan health_score dalam range 0-100
        health_score = max(0, min(100, health_score))
        
        return {
            "overall_health": health_score,
            "issues": issues
        }
    
    def predict(self, audio_bytes: bytes, mode: str) -> Dict[str, Any]:
        """
        Jalankan full prediction pipeline
        
        Args:
            audio_bytes: Raw audio dari frontend
            mode: 'quick' atau 'deep'
            
        Returns:
            Dictionary hasil analisis lengkap
        """
        try:
            # 1. Preprocessing
            logger.info(f"Preprocessing audio in {mode} mode...")
            features = self.preprocess_audio(audio_bytes, mode)
            logger.info(f"Features shape: {features.shape}")
            
            # 2. Predict
            logger.info("Running model inference...")
            prediction = self.model.predict(features, verbose=0)
            logger.info(f"Prediction: {prediction}")
            
            # 3. Interpret
            logger.info("Interpreting results...")
            result = self.interpret_prediction(prediction, mode)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            raise

# Singleton instance
_model_handler = None

def get_model_handler() -> MachineModelHandler:
    """Get atau create model handler instance"""
    global _model_handler
    if _model_handler is None:
        model_path = "models/model.h5"  # Sesuaikan path
        _model_handler = MachineModelHandler(model_path)
    return _model_handler
```

### Step 2: Update Backend FastAPI (main.py)

Buat atau update file `main.py`:

```python
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Dict, Any
import numpy as np
import logging

# Import model handler
from model_handler import get_model_handler, MachineModelHandler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Machine Diagnostics API",
    description="API untuk diagnostik mesin menggunakan model .h5",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PRODUCTION: ganti dengan domain spesifik!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model handler
model_handler: MachineModelHandler = None

# ==================== HELPER FUNCTIONS ====================

def generate_vibration_data(audio_bytes: bytes, mode: str) -> list:
    """Generate vibration data untuk visualisasi di frontend"""
    import librosa
    import io
    
    try:
        # Load audio
        audio_data, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=44100,
            mono=True
        )
        
        # Calculate spectrogram
        hop_length = 512
        n_fft = 2048
        
        stft = librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length)
        magnitude = np.abs(stft)
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        
        # Downsample untuk visualization
        num_points = 100 if mode == 'quick' else 300
        step = max(1, magnitude.shape[1] // num_points)
        
        vibration_data = []
        for i in range(0, magnitude.shape[1], step):
            if len(vibration_data) >= num_points:
                break
            
            mag_frame = magnitude[:, i]
            dominant_freq_idx = np.argmax(mag_frame)
            dominant_freq = freqs[dominant_freq_idx]
            amplitude = float(mag_frame[dominant_freq_idx])
            time_sec = (i * hop_length) / sr
            
            vibration_data.append({
                "time": round(time_sec, 3),
                "amplitude": round(amplitude / 1000, 3),
                "frequency": round(dominant_freq, 2)
            })
        
        return vibration_data
        
    except Exception as e:
        logger.error(f"Error generating vibration data: {e}")
        # Fallback data
        num_points = 100 if mode == 'quick' else 300
        return [
            {
                "time": round(i * 0.01, 3),
                "amplitude": round(np.sin(i * 0.1) * 2 + np.random.random() * 0.5, 3),
                "frequency": round(60 + np.sin(i * 0.05) * 60, 2)
            }
            for i in range(num_points)
        ]

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Machine Diagnostics API with ML Model",
        "version": "1.0.0",
        "model_loaded": model_handler is not None,
        "endpoints": {
            "health": "/api/health",
            "analyze": "/api/analyze",
            "history": "/api/history",
            "docs": "/docs"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "model_loaded": model_handler is not None
    }

@app.post("/api/analyze")
async def analyze_audio(
    file: UploadFile = File(..., description="Audio file"),
    mode: str = Form(..., description="'quick' or 'deep'")
):
    """
    Endpoint utama untuk analisis audio dengan model ML
    """
    global model_handler
    
    logger.info(f"📥 Request received: mode={mode}, file={file.filename}")
    
    # Validasi
    if mode not in ['quick', 'deep']:
        raise HTTPException(
            status_code=400,
            detail="Mode harus 'quick' atau 'deep'"
        )
    
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File tidak valid"
        )
    
    # Check model loaded
    if model_handler is None:
        raise HTTPException(
            status_code=503,
            detail="Model belum dimuat. Restart server."
        )
    
    try:
        # Baca audio
        audio_bytes = await file.read()
        logger.info(f"📊 Audio size: {len(audio_bytes)} bytes")
        
        # Validasi ukuran
        max_size = 50 * 1024 * 1024  # 50MB
        if len(audio_bytes) > max_size:
            raise HTTPException(
                status_code=413,
                detail="File terlalu besar (max 50MB)"
            )
        
        # ===== JALANKAN MODEL ML =====
        logger.info("🤖 Running ML model...")
        prediction_result = model_handler.predict(audio_bytes, mode)
        
        # Generate vibration data
        logger.info("📈 Generating vibration data...")
        vibration_data = generate_vibration_data(audio_bytes, mode)
        
        # Combine results
        result = {
            "overall_health": prediction_result["overall_health"],
            "issues": prediction_result["issues"],
            "vibration_data": vibration_data
        }
        
        logger.info(f"✅ Analysis complete: health={result['overall_health']:.1f}%, issues={len(result['issues'])}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )

@app.get("/api/history")
async def get_history(limit: int = 10):
    """Get analysis history (implement with database)"""
    return {
        "records": [],
        "message": "Database not configured"
    }

# ==================== LIFECYCLE EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Load model saat server start"""
    global model_handler
    
    logger.info("=" * 60)
    logger.info("🚀 Machine Diagnostics API Starting...")
    logger.info("=" * 60)
    
    try:
        logger.info("📦 Loading ML model...")
        model_handler = get_model_handler()
        logger.info("✅ Model loaded successfully!")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        logger.error("⚠️  Server will start but predictions will fail!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup saat shutdown"""
    logger.info("👋 Shutting down...")

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

---

## 🧪 Testing

### 1. Jalankan Backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Output yang diharapkan:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     🚀 Machine Diagnostics API Starting...
INFO:     📦 Loading ML model...
INFO:     ✅ Model berhasil dimuat dari: models/model.h5
INFO:     Input shape: (None, 104)
INFO:     Output shape: (None, 4)
INFO:     ✅ Model loaded successfully!
```

### 2. Test dengan cURL

**Health Check:**
```bash
curl http://localhost:8000/api/health
```

**Test Upload (dengan file audio):**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "file=@test_audio.wav" \
  -F "mode=quick"
```

### 3. Test dengan Frontend

1. Pastikan backend berjalan di `http://localhost:8000`
2. Buka aplikasi frontend Anda
3. Klik tombol "Scan Mesin"
4. Izinkan akses microphone
5. Tunggu recording selesai
6. Lihat hasil diagnosis

### 4. Lihat Dokumentasi API

Buka browser dan akses:
```
http://localhost:8000/docs
```

FastAPI akan menampilkan interactive API documentation (Swagger UI).

---

## 🔍 Troubleshooting

### Problem 1: Model Tidak Bisa Dimuat

**Error:**
```
ValueError: Unknown layer: CustomLayer
```

**Solusi:**
Jika model Anda menggunakan custom layers/objects:

```python
# Di model_handler.py
self.model = tf.keras.models.load_model(
    model_path,
    custom_objects={'CustomLayer': CustomLayer}
)
```

---

### Problem 2: Input Shape Tidak Cocok

**Error:**
```
ValueError: Input shape mismatch. Expected (None, 100) but got (None, 104)
```

**Solusi:**
Sesuaikan feature extraction di `preprocess_audio()` agar jumlah features sama dengan training.

Cek input shape model:
```python
print(model.input_shape)  # (None, 100)
print(features.shape)     # (1, 104) <- harus sama!
```

---

### Problem 3: TensorFlow Warning

**Warning:**
```
Your CPU supports instructions that this TensorFlow binary was not compiled to use
```

**Solusi (opsional):**
```python
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress warnings
```

---

### Problem 4: CORS Error di Frontend

**Error di browser console:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solusi:**
Pastikan CORS sudah diaktifkan di `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Atau ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### Problem 5: Librosa Error

**Error:**
```
audioread.NoBackendError
```

**Solusi:**
Install backend audio:

**Linux:**
```bash
sudo apt-get install ffmpeg libsndfile1
```

**Mac:**
```bash
brew install ffmpeg
```

**Windows:**
Download dan install FFmpeg dari https://ffmpeg.org/download.html

---

## 📊 Menyesuaikan dengan Model Anda

### Langkah Penting:

1. **Cek Input Shape Model**
   ```python
   import tensorflow as tf
   model = tf.keras.models.load_model('model.h5')
   print("Input:", model.input_shape)
   print("Output:", model.output_shape)
   ```

2. **Sesuaikan Preprocessing**
   - Di `preprocess_audio()`, ekstrak features yang SAMA dengan saat training
   - Pastikan jumlah features cocok dengan `model.input_shape`

3. **Sesuaikan Interpretasi**
   - Di `interpret_prediction()`, sesuaikan dengan output model Anda
   - Binary classification? Multi-class? Regression?

4. **Test dengan Data Training**
   - Gunakan salah satu file audio dari dataset training
   - Bandingkan hasil prediksi dengan label asli

---

## 🎯 Checklist Integrasi

- [ ] Model .h5 sudah dicopy ke folder `backend/models/`
- [ ] Dependencies sudah diinstall (`pip install -r requirements.txt`)
- [ ] Preprocessing di `preprocess_audio()` sesuai dengan training
- [ ] Input shape features sama dengan `model.input_shape`
- [ ] Interpretasi di `interpret_prediction()` sesuai output model
- [ ] Backend bisa dijalankan tanpa error
- [ ] Health check endpoint (`/api/health`) return OK
- [ ] Test upload audio berhasil
- [ ] Frontend bisa connect ke backend
- [ ] Hasil prediksi muncul di UI

---

## 💡 Tips Optimasi

1. **Caching Model:**
   Model sudah di-load sekali saat startup (singleton pattern)

2. **Async Processing:**
   Untuk produksi, pertimbangkan async processing:
   ```python
   from fastapi import BackgroundTasks
   
   @app.post("/api/analyze")
   async def analyze(file: UploadFile, background_tasks: BackgroundTasks):
       background_tasks.add_task(process_audio, file)
       return {"status": "processing"}
   ```

3. **GPU Acceleration:**
   Jika server punya GPU:
   ```python
   import tensorflow as tf
   physical_devices = tf.config.list_physical_devices('GPU')
   if physical_devices:
       tf.config.experimental.set_memory_growth(physical_devices[0], True)
   ```

4. **Model Quantization:**
   Untuk inference lebih cepat:
   ```python
   converter = tf.lite.TFLiteConverter.from_keras_model(model)
   converter.optimizations = [tf.lite.Optimize.DEFAULT]
   tflite_model = converter.convert()
   ```

---

## 📞 Bantuan Lebih Lanjut

Jika ada error atau butuh bantuan:

1. Cek logs di console backend
2. Cek browser console untuk error frontend
3. Test endpoint manual dengan Postman atau cURL
4. Periksa dokumentasi Swagger UI di `/docs`

**Struktur error yang informatif sudah diimplementasi di aplikasi Anda!**

---

Selamat mencoba! 🚀
