/**
 * API Service untuk integrasi dengan FastAPI Backend
 * 
 * SETUP BACKEND (FastAPI):
 * 1. Install dependencies: pip install fastapi uvicorn python-multipart
 * 2. Aktifkan CORS di FastAPI:
 *    ```python
 *    from fastapi import FastAPI
 *    from fastapi.middleware.cors import CORSMiddleware
 *    
 *    app = FastAPI()
 *    
 *    app.add_middleware(
 *        CORSMiddleware,
 *        allow_origins=["*"],  # Untuk production, gunakan domain spesifik
 *        allow_credentials=True,
 *        allow_methods=["*"],
 *        allow_headers=["*"],
 *    )
 *    ```
 * 3. Jalankan server: uvicorn main:app --reload --host 0.0.0.0 --port 8000
 */

import { ScanMode, DiagnosisData } from '../App';

// Konfigurasi URL Backend FastAPI
// Ganti dengan URL backend Anda (misalnya: http://localhost:8000 atau https://api.yourserver.com)
const API_BASE_URL = 'http://localhost:8000';

/**
 * Interface untuk response dari FastAPI
 */
export interface FastAPIResponse {
  overall_health: number;
  issues: Array<{
    severity: 'low' | 'medium' | 'high';
    component: string;
    description: string;
    recommendation: string;
  }>;
  vibration_data: Array<{
    time: number;
    amplitude: number;
    frequency: number;
  }>;
}

/**
 * Kirim audio ke FastAPI untuk dianalisis
 * 
 * CONTOH ENDPOINT FASTAPI:
 * ```python
 * @app.post("/api/analyze")
 * async def analyze_audio(
 *     file: UploadFile = File(...),
 *     mode: str = Form(...)
 * ):
 *     # Proses audio dengan model ML Anda
 *     audio_data = await file.read()
 *     
 *     # Jalankan inferensi model
 *     result = your_model.predict(audio_data, mode)
 *     
 *     return {
 *         "overall_health": result["health_score"],
 *         "issues": result["detected_issues"],
 *         "vibration_data": result["vibration_analysis"]
 *     }
 * ```
 */
export async function analyzeAudio(
  audioBlob: Blob,
  mode: ScanMode
): Promise<DiagnosisData> {
  try {
    // Buat FormData untuk upload file
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.wav');
    formData.append('mode', mode);

    // Kirim request ke FastAPI
    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
      // Note: Jangan set Content-Type header, browser akan set otomatis dengan boundary
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result: FastAPIResponse = await response.json();

    // Transform response dari FastAPI ke format DiagnosisData
    const diagnosisData: DiagnosisData = {
      timestamp: new Date().toISOString(),
      mode: mode,
      overallHealth: result.overall_health,
      issues: result.issues.map((issue, index) => ({
        id: index.toString(),
        ...issue
      })),
      vibrationData: result.vibration_data
    };

    return diagnosisData;
  } catch (error) {
    console.error('Error analyzing audio:', error);
    throw new Error('Gagal mengirim data ke server. Periksa koneksi Anda.');
  }
}

/**
 * Check kesehatan server FastAPI
 * 
 * CONTOH ENDPOINT FASTAPI:
 * ```python
 * @app.get("/api/health")
 * async def health_check():
 *     return {"status": "ok", "timestamp": datetime.now().isoformat()}
 * ```
 */
export async function checkServerHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.ok;
  } catch (error) {
    // Silent fail - backend belum running adalah kondisi normal saat development
    return false;
  }
}

/**
 * Simpan rekaman untuk mode offline
 * Rekaman akan disimpan di localStorage dan dikirim nanti saat online
 */
export function saveOfflineRecording(audioBlob: Blob, mode: ScanMode): void {
  const reader = new FileReader();
  reader.onloadend = () => {
    const base64Audio = reader.result as string;
    const recordings = getOfflineRecordings();
    recordings.push({
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      mode: mode,
      audioData: base64Audio
    });
    localStorage.setItem('offline_recordings', JSON.stringify(recordings));
  };
  reader.readAsDataURL(audioBlob);
}

/**
 * Ambil semua rekaman offline
 */
export function getOfflineRecordings(): Array<{
  id: string;
  timestamp: string;
  mode: ScanMode;
  audioData: string;
}> {
  const stored = localStorage.getItem('offline_recordings');
  return stored ? JSON.parse(stored) : [];
}

/**
 * Proses semua rekaman offline saat koneksi kembali
 */
export async function processOfflineRecordings(): Promise<void> {
  const recordings = getOfflineRecordings();
  
  for (const recording of recordings) {
    try {
      // Convert base64 back to Blob
      const response = await fetch(recording.audioData);
      const blob = await response.blob();
      
      // Kirim ke server
      await analyzeAudio(blob, recording.mode);
      
      // Hapus dari localStorage jika berhasil
      const remaining = getOfflineRecordings().filter(r => r.id !== recording.id);
      localStorage.setItem('offline_recordings', JSON.stringify(remaining));
    } catch (error) {
      console.error(`Failed to process offline recording ${recording.id}:`, error);
      // Biarkan di localStorage untuk dicoba lagi nanti
    }
  }
}

/**
 * Get laporan history dari server
 * 
 * CONTOH ENDPOINT FASTAPI:
 * ```python
 * @app.get("/api/history")
 * async def get_history(limit: int = 10):
 *     # Ambil data dari database
 *     records = db.query(DiagnosisRecord).limit(limit).all()
 *     return {"records": records}
 * ```
 */
export async function getAnalysisHistory(limit: number = 10): Promise<DiagnosisData[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/history?limit=${limit}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result.records || [];
  } catch (error) {
    console.error('Error fetching history:', error);
    return [];
  }
}