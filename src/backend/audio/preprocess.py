import librosa
import numpy as np
import io
import soundfile as sf
import cv2

TARGET_SIZE = 128
TARGET_DURATION = 3.0  # detik

def extract_features(wav_bytes: bytes):
    y, sr = sf.read(io.BytesIO(wav_bytes))

    if y.ndim > 1:
        y = y.mean(axis=1)

    # ===============================
    # FIX PANJANG AUDIO
    # ===============================
    target_len = int(TARGET_DURATION * sr)
    if len(y) < target_len:
        y = np.pad(y, (0, target_len - len(y)))
    else:
        y = y[:target_len]

    # ===============================
    # MFCC
    # ===============================
    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=TARGET_SIZE
    )

    mfcc = (mfcc - np.mean(mfcc)) / (np.std(mfcc) + 1e-6)

    mfcc = cv2.resize(
        mfcc,
        (TARGET_SIZE, TARGET_SIZE),
        interpolation=cv2.INTER_AREA
    )

    mfcc = mfcc[..., np.newaxis]
    mfcc = mfcc[np.newaxis, ...]

    return mfcc
