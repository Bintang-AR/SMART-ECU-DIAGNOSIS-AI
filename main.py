from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import logging
import librosa
from pydub import AudioSegment

# ===== Setup logging =====
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

# ===== FastAPI app =====
app = FastAPI(title="Machine Diagnostics API")

# ===== CORS Middleware =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # sesuaikan port frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Health check =====
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

# ===== Dummy ML model =====
class DummyModelHandler:
    def predict(self, y, sr, mode):
        return {"overall_health": 95.0, "issues": []}

model_handler = DummyModelHandler()

# ===== Audio preprocessing =====
def preprocess_audio(audio_bytes: bytes, content_type: str):
    audio_io = BytesIO(audio_bytes)

    try:
        if content_type in ["audio/mpeg", "audio/mp3"]:
            audio = AudioSegment.from_file(audio_io, format="mp3")
        elif content_type == "audio/webm":
            audio = AudioSegment.from_file(audio_io, format="webm")
        else:
            audio = AudioSegment.from_file(audio_io)  # autodetect
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot open audio: {str(e)}")

    # Export ke WAV untuk librosa
    audio_io = BytesIO()
    audio.export(audio_io, format="wav")
    audio_io.seek(0)

    try:
        y, sr = librosa.load(audio_io, sr=None, mono=True)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cannot read audio: {str(e)}")

    return y, sr

# ===== Analyze endpoint =====
@app.post("/api/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    mode: str = Form(...)
):
    logger.info(f"📥 Request received: mode={mode}, file={file.filename}, content_type={file.content_type}")

    if mode not in ["quick", "deep"]:
        raise HTTPException(status_code=400, detail="Mode harus 'quick' atau 'deep'")

    if not file.filename:
        raise HTTPException(status_code=400, detail="File tidak valid")

    audio_bytes = await file.read()
    logger.info(f"📊 Audio size: {len(audio_bytes)} bytes")

    # Max 50MB
    if len(audio_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File terlalu besar (max 50MB)")

    y, sr = preprocess_audio(audio_bytes, file.content_type)

    prediction_result = model_handler.predict(y, sr, mode)
    vibration_data = [0] * 128  # dummy

    result = {
        "overall_health": prediction_result["overall_health"],
        "issues": prediction_result["issues"],
        "vibration_data": vibration_data
    }

    logger.info(f"✅ Analysis complete: health={result['overall_health']}%, issues={len(result['issues'])}")
    return result
