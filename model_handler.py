import tensorflow as tf
import numpy as np
import librosa
import io
from typing import Dict, Any, List
import logging
from io import BytesIO
from pydub import AudioSegment
import librosa

def preprocess_audio(audio_bytes, mode, content_type):
    audio_io = BytesIO(audio_bytes)

    # 1️⃣ Konversi MP3 ke WAV jika perlu
    if content_type in ["audio/mpeg", "audio/mp3"]:
        audio = AudioSegment.from_file(audio_io, format="mp3")
        audio_io = BytesIO()
        audio.export(audio_io, format="wav")
        audio_io.seek(0)

    # 2️⃣ Baca audio pakai librosa
    y, sr = librosa.load(audio_io, sr=None, mono=True)

    # 3️⃣ Lanjut preprocessing untuk ML model
    return y, sr

logger = logging.getLogger(__name__)

class MachineModelHandler:
    """Handler untuk model diagnostik mesin (models/model.h5)"""
    
    def __init__(self, model_path: str):
        """
        Inisialisasi dan load model
        
        Args:
            model_path: models/model.h5
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