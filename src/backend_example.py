"""
Contoh Backend FastAPI untuk Aplikasi Diagnostik Mesin
File ini bisa langsung digunakan sebagai starting point

Cara menggunakan:
1. Simpan file ini sebagai main.py di folder backend
2. Install dependencies: pip install fastapi uvicorn python-multipart librosa numpy
3. Jalankan: uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Dict, Any
import numpy as np
import io
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Machine Diagnostics API",
    description="API untuk analisis diagnostik mesin menggunakan audio",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # UNTUK PRODUCTION: ganti dengan domain spesifik!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== HELPER FUNCTIONS ====================

def analyze_audio_data(audio_bytes: bytes, mode: str) -> Dict[str, Any]:
    """
    Fungsi utama untuk analisis audio
    
    GANTI IMPLEMENTASI INI dengan model ML Anda!
    
    Args:
        audio_bytes: Raw audio data
        mode: 'quick' atau 'deep'
    
    Returns:
        Dictionary berisi hasil analisis
    """
    
    # ===== CONTOH IMPLEMENTASI DENGAN LIBROSA =====
    # Uncomment jika menggunakan librosa untuk preprocessing
    
    # try:
    #     import librosa
    #     
    #     # Load audio
    #     audio_data, sr = librosa.load(io.BytesIO(audio_bytes), sr=44100)
    #     
    #     # Extract features
    #     mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=40)
    #     mfccs_mean = np.mean(mfccs.T, axis=0)
    #     
    #     # Spectral features
    #     spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
    #     spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)
    #     
    #     # Zero crossing rate
    #     zcr = librosa.feature.zero_crossing_rate(audio_data)
    #     
    #     # Combine features
    #     features = np.concatenate([
    #         mfccs_mean,
    #         [np.mean(spectral_centroids)],
    #         [np.mean(spectral_rolloff)],
    #         [np.mean(zcr)]
    #     ])
    #     
    #     # ===== JALANKAN MODEL ML ANDA DI SINI =====
    #     # prediction = your_model.predict(features.reshape(1, -1))
    #     # health_score = float(prediction[0][0] * 100)
    #     
    # except Exception as e:
    #     logger.error(f"Error in audio processing: {e}")
    #     raise
    
    # ===== DUMMY RESPONSE UNTUK TESTING =====
    # Ganti dengan hasil model Anda
    
    logger.info(f"Processing audio in {mode} mode")
    
    # Simulasi health score berdasarkan mode
    health_score = 78 if mode == 'quick' else 72
    
    # Simulasi deteksi masalah
    if mode == 'quick':
        issues = [
            {
                "severity": "medium",
                "component": "Bearing Motor",
                "description": "Terdeteksi getaran abnormal pada frekuensi 120 Hz",
                "recommendation": "Lakukan inspeksi visual dan pelumasan dalam 7 hari"
            }
        ]
    else:
        issues = [
            {
                "severity": "high",
                "component": "Bearing Motor",
                "description": "Terdeteksi getaran abnormal pada frekuensi 120 Hz dengan amplitudo tinggi",
                "recommendation": "Segera lakukan penggantian bearing dalam 48 jam"
            },
            {
                "severity": "medium",
                "component": "Belt Transmisi",
                "description": "Ketegangan belt tidak merata, terdeteksi dari pola getaran",
                "recommendation": "Sesuaikan ketegangan belt pada maintenance berikutnya"
            },
            {
                "severity": "low",
                "component": "Mounting Base",
                "description": "Sedikit getaran resonansi pada mounting",
                "recommendation": "Monitor secara berkala, belum perlu tindakan"
            }
        ]
    
    # Generate vibration data
    num_points = 100 if mode == 'quick' else 300
    vibration_data = [
        {
            "time": round(i * 0.01, 3),
            "amplitude": round(np.sin(i * 0.1) * 2 + np.random.random() * 0.5, 3),
            "frequency": round(60 + np.sin(i * 0.05) * 60, 2)
        }
        for i in range(num_points)
    ]
    
    return {
        "overall_health": health_score,
        "issues": issues,
        "vibration_data": vibration_data
    }

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Machine Diagnostics API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "analyze": "/api/analyze",
            "history": "/api/history",
            "docs": "/docs"
        }
    }

@app.get("/api/health")
async def health_check():
    """
    Endpoint untuk cek kesehatan server
    Frontend menggunakan ini untuk deteksi offline mode
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "message": "Server is running"
    }

@app.post("/api/analyze")
async def analyze_audio(
    file: UploadFile = File(..., description="Audio file (webm/wav format)"),
    mode: str = Form(..., description="Scan mode: 'quick' or 'deep'")
):
    """
    Endpoint utama untuk analisis audio mesin
    
    Parameters:
    - file: Audio file dari frontend
    - mode: 'quick' (5s) atau 'deep' (15s)
    
    Returns:
    - overall_health: Health score 0-100
    - issues: List masalah yang terdeteksi
    - vibration_data: Data getaran untuk visualisasi
    """
    
    logger.info(f"Received analysis request: mode={mode}, filename={file.filename}")
    
    # Validasi mode
    if mode not in ['quick', 'deep']:
        raise HTTPException(
            status_code=400,
            detail="Mode harus 'quick' atau 'deep'"
        )
    
    # Validasi file
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="File tidak valid"
        )
    
    try:
        # Baca file audio
        audio_bytes = await file.read()
        logger.info(f"Audio file size: {len(audio_bytes)} bytes")
        
        # Validasi ukuran file (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if len(audio_bytes) > max_size:
            raise HTTPException(
                status_code=413,
                detail="File terlalu besar (max 50MB)"
            )
        
        # Proses audio
        result = analyze_audio_data(audio_bytes, mode)
        
        logger.info(f"Analysis completed: health={result['overall_health']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memproses audio: {str(e)}"
        )

@app.get("/api/history")
async def get_history(limit: int = 10):
    """
    Endpoint untuk mengambil riwayat analisis
    
    Note: Implementasi ini memerlukan database (PostgreSQL, MongoDB, dll)
    Untuk saat ini, return empty list
    """
    
    # TODO: Implementasi dengan database
    # from database import get_diagnosis_records
    # records = get_diagnosis_records(limit=limit)
    
    logger.info(f"History request: limit={limit}")
    
    return {
        "records": [],
        "message": "Database not configured. Implement this with your database."
    }

# ==================== STARTUP/SHUTDOWN EVENTS ====================

@app.on_event("startup")
async def startup_event():
    """Event yang dijalankan saat server start"""
    logger.info("=" * 50)
    logger.info("Machine Diagnostics API Starting...")
    logger.info("=" * 50)
    
    # TODO: Load ML model saat startup
    # global model
    # model = load_model('path/to/model.h5')
    # logger.info("Model loaded successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Event yang dijalankan saat server shutdown"""
    logger.info("Shutting down Machine Diagnostics API...")

# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Endpoint tidak ditemukan",
        "detail": "Periksa URL dan method yang digunakan",
        "docs": "/docs"
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal server error",
        "detail": "Terjadi kesalahan pada server"
    }

# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    # Development configuration
    uvicorn.run(
        "main:app",  # Ganti dengan nama file Anda jika bukan main.py
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload saat file berubah
        log_level="info"
    )
    
    # Production configuration (uncomment untuk production):
    # uvicorn.run(
    #     "main:app",
    #     host="0.0.0.0",
    #     port=8000,
    #     workers=4,  # Jumlah worker processes
    #     log_level="info",
    #     access_log=True
    # )
