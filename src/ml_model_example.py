"""
Contoh Integrasi Model Machine Learning untuk Diagnostik Mesin
File ini menunjukkan berbagai cara mengintegrasikan model ML dengan FastAPI

Pilih implementasi yang sesuai dengan framework ML Anda:
1. TensorFlow/Keras
2. PyTorch
3. Scikit-learn
"""

import numpy as np
import librosa
from typing import Dict, Any, Tuple
import io

# ============================================================
# CONTOH 1: TensorFlow/Keras Model
# ============================================================

class TensorFlowModelHandler:
    """Handler untuk model TensorFlow/Keras"""
    
    def __init__(self, model_path: str):
        """
        Initialize model
        
        Args:
            model_path: Path ke file model (.h5 atau SavedModel)
        """
        import tensorflow as tf
        
        self.model = tf.keras.models.load_model(model_path)
        print(f"TensorFlow model loaded from {model_path}")
        print(f"Model input shape: {self.model.input_shape}")
        print(f"Model output shape: {self.model.output_shape}")
    
    def preprocess_audio(self, audio_bytes: bytes, mode: str) -> np.ndarray:
        """
        Preprocessing audio untuk model
        
        Args:
            audio_bytes: Raw audio data
            mode: 'quick' atau 'deep'
        
        Returns:
            Features array siap untuk model
        """
        # Load audio
        audio_data, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=44100,
            mono=True
        )
        
        # Extract MFCC features (40 coefficients)
        mfccs = librosa.feature.mfcc(
            y=audio_data,
            sr=sr,
            n_mfcc=40,
            n_fft=2048,
            hop_length=512
        )
        
        # Mean dan standard deviation
        mfccs_mean = np.mean(mfccs.T, axis=0)
        mfccs_std = np.std(mfccs.T, axis=0)
        
        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)
        
        # Tempo
        tempo, _ = librosa.beat.beat_track(y=audio_data, sr=sr)
        
        # Combine all features
        features = np.concatenate([
            mfccs_mean,
            mfccs_std,
            [np.mean(spectral_centroid)],
            [np.std(spectral_centroid)],
            [np.mean(spectral_rolloff)],
            [np.mean(spectral_bandwidth)],
            [np.mean(zcr)],
            [tempo]
        ])
        
        # Reshape untuk model (1, num_features)
        return features.reshape(1, -1)
    
    def predict(self, audio_bytes: bytes, mode: str) -> Dict[str, Any]:
        """
        Jalankan prediksi
        
        Returns:
            Dictionary hasil analisis
        """
        # Preprocess
        features = self.preprocess_audio(audio_bytes, mode)
        
        # Predict
        prediction = self.model.predict(features, verbose=0)
        
        # Interpretasi hasil
        # Asumsi model output: [health_score, bearing_fault, belt_fault, mounting_fault]
        health_score = float(prediction[0][0] * 100)
        bearing_prob = float(prediction[0][1])
        belt_prob = float(prediction[0][2])
        mounting_prob = float(prediction[0][3])
        
        # Generate issues based on probabilities
        issues = []
        
        if bearing_prob > 0.7:
            issues.append({
                "severity": "high",
                "component": "Bearing Motor",
                "description": f"Terdeteksi masalah bearing (confidence: {bearing_prob:.1%})",
                "recommendation": "Segera lakukan penggantian bearing dalam 48 jam"
            })
        elif bearing_prob > 0.4:
            issues.append({
                "severity": "medium",
                "component": "Bearing Motor",
                "description": f"Kemungkinan masalah bearing (confidence: {bearing_prob:.1%})",
                "recommendation": "Lakukan inspeksi dalam 7 hari"
            })
        
        if belt_prob > 0.5:
            issues.append({
                "severity": "medium",
                "component": "Belt Transmisi",
                "description": f"Terdeteksi masalah belt (confidence: {belt_prob:.1%})",
                "recommendation": "Sesuaikan ketegangan belt"
            })
        
        if mounting_prob > 0.3:
            issues.append({
                "severity": "low",
                "component": "Mounting Base",
                "description": f"Getaran pada mounting (confidence: {mounting_prob:.1%})",
                "recommendation": "Monitor secara berkala"
            })
        
        return {
            "overall_health": max(0, min(100, health_score)),
            "issues": issues,
            "raw_prediction": {
                "bearing_prob": bearing_prob,
                "belt_prob": belt_prob,
                "mounting_prob": mounting_prob
            }
        }

# ============================================================
# CONTOH 2: PyTorch Model
# ============================================================

class PyTorchModelHandler:
    """Handler untuk model PyTorch"""
    
    def __init__(self, model_path: str):
        """Initialize PyTorch model"""
        import torch
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = torch.load(model_path, map_location=self.device)
        self.model.eval()
        
        print(f"PyTorch model loaded from {model_path}")
        print(f"Using device: {self.device}")
    
    def preprocess_audio(self, audio_bytes: bytes, mode: str) -> 'torch.Tensor':
        """Preprocessing untuk PyTorch"""
        import torch
        
        # Load audio
        audio_data, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=44100,
            mono=True
        )
        
        # Extract mel-spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio_data,
            sr=sr,
            n_mels=128,
            n_fft=2048,
            hop_length=512
        )
        
        # Convert to dB
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        
        # Normalize
        mel_spec_db = (mel_spec_db - mel_spec_db.mean()) / mel_spec_db.std()
        
        # Convert to tensor
        tensor = torch.from_numpy(mel_spec_db).float()
        tensor = tensor.unsqueeze(0).unsqueeze(0)  # Add batch and channel dims
        
        return tensor.to(self.device)
    
    def predict(self, audio_bytes: bytes, mode: str) -> Dict[str, Any]:
        """Jalankan prediksi dengan PyTorch"""
        import torch
        
        # Preprocess
        features = self.preprocess_audio(audio_bytes, mode)
        
        # Predict
        with torch.no_grad():
            output = self.model(features)
            probabilities = torch.softmax(output, dim=1)
        
        # Convert to numpy
        probs = probabilities.cpu().numpy()[0]
        
        # Interpretasi (contoh untuk 4 class: normal, bearing, belt, mounting)
        classes = ["normal", "bearing", "belt", "mounting"]
        predicted_class = classes[np.argmax(probs)]
        confidence = float(np.max(probs))
        
        health_score = 100 - (probs[1:].sum() * 100)  # Reduce based on fault probs
        
        issues = []
        if predicted_class == "bearing" or probs[1] > 0.3:
            issues.append({
                "severity": "high" if probs[1] > 0.7 else "medium",
                "component": "Bearing Motor",
                "description": f"Terdeteksi masalah bearing (confidence: {probs[1]:.1%})",
                "recommendation": "Lakukan inspeksi bearing"
            })
        
        if predicted_class == "belt" or probs[2] > 0.3:
            issues.append({
                "severity": "medium",
                "component": "Belt Transmisi",
                "description": f"Terdeteksi masalah belt (confidence: {probs[2]:.1%})",
                "recommendation": "Periksa ketegangan belt"
            })
        
        return {
            "overall_health": float(health_score),
            "issues": issues,
            "raw_prediction": {
                "predicted_class": predicted_class,
                "confidence": confidence,
                "probabilities": {cls: float(prob) for cls, prob in zip(classes, probs)}
            }
        }

# ============================================================
# CONTOH 3: Scikit-learn Model
# ============================================================

class ScikitLearnModelHandler:
    """Handler untuk model Scikit-learn"""
    
    def __init__(self, model_path: str):
        """Initialize scikit-learn model"""
        import joblib
        
        self.model = joblib.load(model_path)
        print(f"Scikit-learn model loaded from {model_path}")
    
    def extract_features(self, audio_bytes: bytes) -> np.ndarray:
        """Extract audio features"""
        # Load audio
        audio_data, sr = librosa.load(
            io.BytesIO(audio_bytes),
            sr=44100,
            mono=True
        )
        
        # MFCC
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=20)
        mfccs_mean = np.mean(mfccs, axis=1)
        mfccs_var = np.var(mfccs, axis=1)
        
        # Chroma
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)
        
        # Spectral contrast
        contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
        contrast_mean = np.mean(contrast, axis=1)
        
        # Combine all features
        features = np.concatenate([
            mfccs_mean,
            mfccs_var,
            chroma_mean,
            contrast_mean
        ])
        
        return features.reshape(1, -1)
    
    def predict(self, audio_bytes: bytes, mode: str) -> Dict[str, Any]:
        """Jalankan prediksi"""
        # Extract features
        features = self.extract_features(audio_bytes)
        
        # Predict
        prediction = self.model.predict(features)[0]
        
        # Jika model support probability
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features)[0]
        else:
            probabilities = None
        
        # Generate response
        health_score = 85 if prediction == 0 else 65  # 0 = normal, 1 = fault
        
        issues = []
        if prediction == 1:
            issues.append({
                "severity": "medium",
                "component": "Motor",
                "description": "Terdeteksi anomali pada mesin",
                "recommendation": "Lakukan pemeriksaan lebih lanjut"
            })
        
        result = {
            "overall_health": float(health_score),
            "issues": issues
        }
        
        if probabilities is not None:
            result["raw_prediction"] = {
                "class": int(prediction),
                "probabilities": probabilities.tolist()
            }
        
        return result

# ============================================================
# GENERATE VIBRATION DATA
# ============================================================

def generate_vibration_data(audio_bytes: bytes, mode: str) -> list:
    """
    Generate vibration data untuk visualisasi
    
    Args:
        audio_bytes: Audio data
        mode: 'quick' atau 'deep'
    
    Returns:
        List of vibration data points
    """
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
        
        # Calculate dominant frequency at each time frame
        freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
        
        # Downsample untuk visualization
        num_points = 100 if mode == 'quick' else 300
        step = max(1, magnitude.shape[1] // num_points)
        
        vibration_data = []
        for i in range(0, magnitude.shape[1], step):
            if len(vibration_data) >= num_points:
                break
                
            # Get magnitude spectrum at this time
            mag_frame = magnitude[:, i]
            
            # Find dominant frequency
            dominant_freq_idx = np.argmax(mag_frame)
            dominant_freq = freqs[dominant_freq_idx]
            
            # Amplitude is the magnitude at dominant frequency
            amplitude = float(mag_frame[dominant_freq_idx])
            
            # Time in seconds
            time_sec = (i * hop_length) / sr
            
            vibration_data.append({
                "time": round(time_sec, 3),
                "amplitude": round(amplitude / 1000, 3),  # Normalize
                "frequency": round(dominant_freq, 2)
            })
        
        return vibration_data
        
    except Exception as e:
        print(f"Error generating vibration data: {e}")
        # Fallback to synthetic data
        num_points = 100 if mode == 'quick' else 300
        return [
            {
                "time": round(i * 0.01, 3),
                "amplitude": round(np.sin(i * 0.1) * 2 + np.random.random() * 0.5, 3),
                "frequency": round(60 + np.sin(i * 0.05) * 60, 2)
            }
            for i in range(num_points)
        ]

# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == "__main__":
    """
    Contoh cara menggunakan model handlers
    """
    
    # Pilih salah satu:
    
    # 1. TensorFlow
    # handler = TensorFlowModelHandler("models/tensorflow_model.h5")
    
    # 2. PyTorch
    # handler = PyTorchModelHandler("models/pytorch_model.pt")
    
    # 3. Scikit-learn
    # handler = ScikitLearnModelHandler("models/sklearn_model.pkl")
    
    # Load test audio
    # with open("test_audio.wav", "rb") as f:
    #     audio_bytes = f.read()
    
    # Run prediction
    # result = handler.predict(audio_bytes, mode="quick")
    # print(result)
    
    # Generate vibration data
    # vibration = generate_vibration_data(audio_bytes, mode="quick")
    # print(f"Generated {len(vibration)} vibration data points")
    
    pass
