from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from services.inference import run_inference
from utils.vibration import generate_vibration_data

app = FastAPI(title="Machine Diagnostics API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }

# ===============================
# ISSUE MAPPING
# ===============================
ISSUE_MAP = {
    "misfire": {
        "severity": "high",
        "component": "Sistem Pembakaran",
        "description": "Terjadi misfire pada mesin",
        "recommendation": "Periksa busi, injector, dan sistem bahan bakar"
    },
    "buka_suara_mesin": {
        "severity": "medium",
        "component": "Celah Mesin",
        "description": "Suara mesin terbuka tidak normal",
        "recommendation": "Periksa celah katup dan mounting mesin"
    },
    "oli_rendah": {
        "severity": "medium",
        "component": "Pelumasan",
        "description": "Indikasi oli rendah atau aus",
        "recommendation": "Cek dan tambah oli mesin"
    },
    "knocking": {
        "severity": "high",
        "component": "Ruang Bakar",
        "description": "Knocking terdeteksi",
        "recommendation": "Gunakan BBM oktan lebih tinggi dan cek timing pengapian"
    },
    "pengapian_buruk": {
        "severity": "medium",
        "component": "Pengapian",
        "description": "Sistem pengapian tidak optimal",
        "recommendation": "Periksa koil dan busi"
    }
}

@app.post("/api/analyze")
async def analyze_audio(
    file: UploadFile = File(...),
    mode: str = Form(...)
):
    audio_bytes = await file.read()

    # ===============================
    # SAFE INFERENCE
    # ===============================
    try:
        label, confidence, probabilities = run_inference(audio_bytes)
    except Exception as e:
        print("❌ Inference error:", e)
        label = "unknown"
        confidence = 0.0
        probabilities = {}

    # ===============================
    # VALIDATION (INI KUNCI FIX)
    # ===============================
    VALID_CONFIDENCE_THRESHOLD = 0.60

    issues = []

    if (
        label in ISSUE_MAP
        and confidence >= VALID_CONFIDENCE_THRESHOLD
    ):
        issue = ISSUE_MAP[label].copy()
        issue["id"] = label
        issues.append(issue)
    else:
        label = "normal"

    # ===============================
    # HEALTH LOGIC
    # ===============================
    if label == "normal":
        overall_health = int(90 + confidence * 10)   # 90–100
    else:
        overall_health = max(30, int((1 - confidence) * 100))

    vibration_data = generate_vibration_data(
        100 if mode == "quick" else 300
    )

    response = {
        "overallHealth": overall_health,
        "detectedClass": label,
        "confidence": round(confidence, 4),
        "classProbabilities": probabilities,
        "issues": issues,
        "vibrationData": vibration_data,
        "timestamp": datetime.now().isoformat(),
        "mode": mode
    }

    # ===============================
    # DEBUG LOG (PENTING)
    # ===============================
    print("=== ANALYSIS RESULT ===")
    print("Label       :", label)
    print("Confidence  :", confidence)
    print("Issues      :", issues)
    print("=======================")

    return response
