import librosa
import numpy as np
import io
import soundfile as sf
import cv2

TARGET_SIZE = 128

def extract_features(wav_bytes: bytes):
    # ===============================
    # LOAD AUDIO
    # ===============================
    y, sr = sf.read(io.BytesIO(wav_bytes))

    # Convert ke mono
    if y.ndim > 1:
        y = y.mean(axis=1)

    # ===============================
    # MFCC
    # ===============================
    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=TARGET_SIZE
    )

    # ===============================
    # NORMALISASI
    # ===============================
    mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-6)

    # ===============================
    # RESIZE → 128x128
    # ===============================
    mfcc_resized = cv2.resize(
        mfcc,
        (TARGET_SIZE, TARGET_SIZE),
        interpolation=cv2.INTER_AREA
    )

    # ===============================
    # SHAPE CNN
    # (1, 128, 128, 1)
    # ===============================
    mfcc_resized = mfcc_resized[..., np.newaxis]
    mfcc_resized = mfcc_resized[np.newaxis, ...]

    return mfcc_resized
