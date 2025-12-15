import { ScanMode, DiagnosisData } from "../App";

/* ============================
   CONFIG
============================ */
const API_BASE = "http://127.0.0.1:8000";

/* ============================
   HEALTH CHECK
============================ */
export async function checkServerHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    return res.ok;
  } catch {
    return false;
  }
}

/* ============================
   ANALYZE AUDIO (REAL BACKEND)
============================ */
export async function analyzeAudio(
  audioBlob: Blob,
  mode: ScanMode
): Promise<DiagnosisData> {
  const formData = new FormData();

  // ⬇️ penting: backend FastAPI terima UploadFile
  formData.append("file", audioBlob, "recording.webm");
  formData.append("mode", mode);

  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Gagal menganalisis audio");
  }

  const data = await res.json();

  return {
    timestamp: data.timestamp,
    mode: data.mode,
    overallHealth: data.overallHealth,
    issues: data.issues,
    vibrationData: data.vibrationData,
  };
}

/* ============================
   OFFLINE STORAGE (OPTIONAL)
============================ */
export function saveOfflineRecording(blob: Blob, mode: ScanMode) {
  const key = `offline_recording_${Date.now()}`;
  const record = {
    mode,
    blob,
    timestamp: new Date().toISOString(),
  };

  // NOTE: Blob tidak bisa langsung disimpan di localStorage
  // Ini placeholder (idealnya pakai IndexedDB)
  console.warn("Offline recording saved (mock):", key, record);
}

export async function processOfflineRecordings() {
  // Placeholder untuk future sync
  console.info("Processing offline recordings...");
}
