from models.predictor import SoundModel
from audio.convert import webm_to_wav
from audio.preprocess import extract_features
import numpy as np

CLASSES = [
    "normal",
    "misfire",
    "buka_suara_mesin",
    "oli_rendah",
    "knocking",
    "pengapian_buruk",
    "aki_tekor",
    "power_steering",
    "serpentine_belt"
]

model = SoundModel()

def run_inference(audio_bytes: bytes):
    wav_bytes = webm_to_wav(audio_bytes)
    features = extract_features(wav_bytes)

    preds = model.predict(features)
    preds = np.squeeze(preds)

    if preds.ndim != 1 or len(preds) != len(CLASSES):
        raise ValueError(f"Output model tidak valid: {preds.shape}")

    preds = np.clip(preds, 1e-6, 1.0)
    preds = preds / np.sum(preds)

    class_index = int(np.argmax(preds))
    label = CLASSES[class_index]
    confidence = float(preds[class_index])

    probabilities = {
        CLASSES[i]: round(float(preds[i]), 4)
        for i in range(len(CLASSES))
    }

    return label, confidence, probabilities
