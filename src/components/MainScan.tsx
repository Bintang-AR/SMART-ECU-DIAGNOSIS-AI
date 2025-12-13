import { useState, useRef, useEffect } from 'react';
import { Mic, Settings, Wifi, WifiOff, Info, X } from 'lucide-react';
import { ScanMode, DiagnosisData } from '../App';
import { 
  analyzeAudio, 
  checkServerHealth, 
  saveOfflineRecording,
  processOfflineRecordings 
} from '../services/api';

interface MainScanProps {
  onScanComplete: (data: DiagnosisData) => void;
  isOffline: boolean;
  setIsOffline: (offline: boolean) => void;
}

export function MainScan({ onScanComplete, isOffline, setIsOffline }: MainScanProps) {
  const [selectedMode, setSelectedMode] = useState<ScanMode>('quick');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingProgress, setRecordingProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [showBackendInfo, setShowBackendInfo] = useState(false);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Check server health saat komponen mount
  useEffect(() => {
    // Hanya check jika dalam mode online
    if (!isOffline) {
      checkServerHealth().then(isHealthy => {
        if (!isHealthy) {
          // Backend belum running - tampilkan info banner saja
          setShowBackendInfo(true);
        } else {
          // Backend tersedia
          setShowBackendInfo(false);
        }
      });
    } else {
      setShowBackendInfo(false);
    }
  }, [isOffline]);

  // Proses rekaman offline saat kembali online
  useEffect(() => {
    if (!isOffline) {
      processOfflineRecordings().catch(() => {
        // Silent - tidak perlu log jika gagal
      });
    }
  }, [isOffline]);

  const handleStartScan = async () => {
    setError(null);
    
    try {
      // Minta izin akses microphone
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
          sampleRate: 44100
        } 
      });

      // Setup MediaRecorder untuk merekam audio
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      // Event handler saat ada data audio
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      // Event handler saat recording selesai
      mediaRecorder.onstop = async () => {
        // Hentikan stream microphone
        stream.getTracks().forEach(track => track.stop());

        // Gabungkan semua chunks menjadi satu Blob
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        setIsProcessing(true);

        try {
          if (isOffline) {
            // Mode offline: simpan rekaman lokal
            saveOfflineRecording(audioBlob, selectedMode);
            
            // Generate mock data untuk preview
            const mockData = generateMockDiagnosisData(selectedMode);
            onScanComplete(mockData);
            
            setError('Rekaman disimpan. Data akan diproses saat online.');
          } else {
            // Mode online: kirim ke FastAPI server
            const diagnosisData = await analyzeAudio(audioBlob, selectedMode);
            onScanComplete(diagnosisData);
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Terjadi kesalahan saat memproses audio');
          
          // Fallback ke mock data jika API gagal
          const mockData = generateMockDiagnosisData(selectedMode);
          onScanComplete(mockData);
        } finally {
          setIsProcessing(false);
        }
      };

      // Mulai recording
      setIsRecording(true);
      setRecordingProgress(0);
      mediaRecorder.start();

      // Durasi recording berdasarkan mode
      const duration = selectedMode === 'quick' ? 5000 : 15000; // 5s atau 15s
      const interval = 100; // Update setiap 100ms
      const steps = duration / interval;
      let currentStep = 0;

      // Update progress bar
      const progressInterval = setInterval(() => {
        currentStep++;
        const progress = (currentStep / steps) * 100;
        setRecordingProgress(progress);

        if (progress >= 100) {
          clearInterval(progressInterval);
          mediaRecorder.stop();
          setIsRecording(false);
        }
      }, interval);

    } catch (err) {
      // Handle different microphone errors
      if (err instanceof Error) {
        if (err.name === 'NotAllowedError') {
          setError('Izin microphone ditolak. Klik ikon kunci/info di address bar untuk memberikan izin.');
        } else if (err.name === 'NotFoundError') {
          setError('Microphone tidak ditemukan. Pastikan device memiliki microphone.');
        } else if (err.name === 'NotReadableError') {
          setError('Microphone sedang digunakan aplikasi lain. Tutup aplikasi tersebut dan coba lagi.');
        } else {
          setError('Gagal mengakses microphone. Coba refresh halaman dan izinkan akses microphone.');
        }
      } else {
        setError('Gagal mengakses microphone. Pastikan browser mendukung recording audio.');
      }
    }
  };

  const generateMockDiagnosisData = (mode: ScanMode): DiagnosisData => {
    return {
      timestamp: new Date().toISOString(),
      mode: mode,
      overallHealth: mode === 'quick' ? 78 : 72,
      issues: mode === 'quick' 
        ? [
            {
              id: '1',
              severity: 'medium',
              component: 'Bearing Motor',
              description: 'Terdeteksi getaran abnormal pada frekuensi 120 Hz',
              recommendation: 'Lakukan inspeksi visual dan pelumasan dalam 7 hari'
            }
          ]
        : [
            {
              id: '1',
              severity: 'high',
              component: 'Bearing Motor',
              description: 'Terdeteksi getaran abnormal pada frekuensi 120 Hz dengan amplitudo tinggi',
              recommendation: 'Segera lakukan penggantian bearing dalam 48 jam'
            },
            {
              id: '2',
              severity: 'medium',
              component: 'Belt Transmisi',
              description: 'Ketegangan belt tidak merata, terdeteksi dari pola getaran',
              recommendation: 'Sesuaikan ketegangan belt pada maintenance berikutnya'
            },
            {
              id: '3',
              severity: 'low',
              component: 'Mounting Base',
              description: 'Sedikit getaran resonansi pada mounting',
              recommendation: 'Monitor secara berkala, belum perlu tindakan'
            }
          ],
      vibrationData: generateMockVibrationData(mode)
    };
  };

  const generateMockVibrationData = (mode: ScanMode) => {
    const dataPoints = mode === 'quick' ? 100 : 300;
    return Array.from({ length: dataPoints }, (_, i) => ({
      time: i * 0.01,
      amplitude: Math.sin(i * 0.1) * 2 + Math.random() * 0.5 + (i > 50 ? Math.sin(i * 0.05) * 1.5 : 0),
      frequency: 60 + Math.sin(i * 0.05) * 60
    }));
  };

  return (
    <div className="min-h-screen bg-black p-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-white mb-1">Diagnostik Mesin AI</h1>
            <p className="text-gray-400">Analisis kondisi mesin dengan teknologi suara</p>
          </div>
          <button
            onClick={() => setIsOffline(!isOffline)}
            className={`p-3 rounded-full ${isOffline ? 'bg-red-900 text-red-400' : 'bg-green-900 text-green-400'}`}
          >
            {isOffline ? <WifiOff className="w-6 h-6" /> : <Wifi className="w-6 h-6" />}
          </button>
        </div>

        {/* Offline Warning */}
        {isOffline && (
          <div className="bg-amber-900 border border-amber-700 rounded-lg p-4 mb-6 flex items-start gap-3">
            <Info className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-amber-200">Mode Offline Aktif</p>
              <p className="text-amber-300 text-sm mt-1">
                Rekaman akan disimpan secara lokal dan diproses saat koneksi tersedia
              </p>
            </div>
          </div>
        )}

        {/* Mode Selection */}
        <div className="bg-gray-800 rounded-2xl shadow-lg p-6 mb-6">
          <label className="block text-gray-300 mb-4">Pilih Mode Pemindaian</label>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => !isRecording && setSelectedMode('quick')}
              disabled={isRecording}
              className={`p-6 rounded-xl border-2 transition-all ${
                selectedMode === 'quick'
                  ? 'border-red-500 bg-red-900/30'
                  : 'border-gray-600 hover:border-gray-500'
              } ${isRecording ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className="flex items-center justify-center mb-3">
                <Settings className="w-8 h-8 text-red-500" />
              </div>
              <h3 className="text-white mb-2">Quick Scan</h3>
              <p className="text-gray-400 text-sm">Pemindaian cepat (5 detik)</p>
              <p className="text-gray-500 text-sm mt-1">Deteksi masalah umum</p>
            </button>

            <button
              onClick={() => !isRecording && setSelectedMode('deep')}
              disabled={isRecording}
              className={`p-6 rounded-xl border-2 transition-all ${
                selectedMode === 'deep'
                  ? 'border-red-500 bg-red-900/30'
                  : 'border-gray-600 hover:border-gray-500'
              } ${isRecording ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className="flex items-center justify-center mb-3">
                <Settings className="w-8 h-8 text-red-500" />
              </div>
              <h3 className="text-white mb-2">Deep Scan</h3>
              <p className="text-gray-400 text-sm">Pemindaian mendalam (15 detik)</p>
              <p className="text-gray-500 text-sm mt-1">Analisis komprehensif</p>
            </button>
          </div>
        </div>

        {/* Recording Instructions */}
        <div className="bg-gray-800 rounded-2xl shadow-lg p-6 mb-6">
          <h3 className="text-white mb-3">Cara Merekam</h3>
          <ul className="space-y-2 text-gray-300">
            <li className="flex items-start gap-2">
              <span className="text-red-500 flex-shrink-0">1.</span>
              <span>Dekatkan mikrofon ke mesin yang beroperasi (jarak 10-30 cm)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-500 flex-shrink-0">2.</span>
              <span>Pastikan area sekitar relatif tenang</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-500 flex-shrink-0">3.</span>
              <span>Tekan tombol Scan Mesin dan tahan posisi stabil</span>
            </li>
          </ul>
        </div>

        {/* Main Scan Button */}
        <div className="relative">
          {isRecording ? (
            <div className="bg-gray-800 rounded-2xl shadow-lg p-8">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-red-900 rounded-full mb-4 animate-pulse">
                  <Mic className="w-10 h-10 text-red-500" />
                </div>
                <h3 className="text-white mb-2">Sedang Merekam...</h3>
                <p className="text-gray-400">Jaga posisi mikrofon tetap stabil</p>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-red-600 h-full transition-all duration-300 rounded-full"
                  style={{ width: `${recordingProgress}%` }}
                />
              </div>
              <p className="text-center text-gray-400 text-sm mt-2">{recordingProgress}%</p>
            </div>
          ) : (
            <button
              onClick={handleStartScan}
              className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white rounded-2xl shadow-xl p-8 transition-all transform hover:scale-105 active:scale-95"
            >
              <div className="flex items-center justify-center gap-4">
                <Mic className="w-12 h-12" />
                <div className="text-left">
                  <h2 className="text-white mb-1">Scan Mesin</h2>
                  <p className="text-red-100">
                    {selectedMode === 'quick' ? 'Mulai Quick Scan' : 'Mulai Deep Scan'}
                  </p>
                </div>
              </div>
            </button>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900 border border-red-700 rounded-lg p-4 mt-6 flex items-start gap-3">
            <Info className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-red-200">Error</p>
              <p className="text-red-300 text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Backend Info */}
        {showBackendInfo && (
          <div className="bg-amber-900 border border-amber-700 rounded-lg p-4 mt-6 flex items-start gap-3">
            <Info className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-amber-200">Backend FastAPI belum running</p>
              <p className="text-amber-300 text-sm mt-1">
                Gunakan mode offline atau jalankan backend di http://localhost:8000
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}