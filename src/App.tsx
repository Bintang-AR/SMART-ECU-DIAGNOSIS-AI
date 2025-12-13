import { useState } from 'react';
import { MainScan } from './components/MainScan';
import { DiagnosisResults } from './components/DiagnosisResults';
import { SpectrogramViewer } from './components/SpectrogramViewer';

export type ScanMode = 'quick' | 'deep';

export interface DiagnosisData {
  timestamp: string;
  mode: ScanMode;
  overallHealth: number;
  issues: Array<{
    id: string;
    severity: 'low' | 'medium' | 'high';
    component: string;
    description: string;
    recommendation: string;
  }>;
  vibrationData: Array<{
    time: number;
    amplitude: number;
    frequency: number;
  }>;
}

export default function App() {
  const [currentView, setCurrentView] = useState<'scan' | 'results' | 'spectrogram'>('scan');
  const [diagnosisData, setDiagnosisData] = useState<DiagnosisData | null>(null);
  const [isOffline, setIsOffline] = useState(false);

  const handleScanComplete = async (file: File, mode: ScanMode) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('mode', mode);

      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Backend error: ${response.status}`);
      }

      const data = await response.json();
      setDiagnosisData(data);
      setCurrentView('results');
    } catch (err) {
      console.error('Error scanning audio:', err);
      alert('Gagal melakukan scan. Pastikan backend berjalan dan file audio valid.');
      setIsOffline(true);
    }
  };

  const handleViewSpectrogram = () => {
    setCurrentView('spectrogram');
  };

  const handleBackToScan = () => {
    setCurrentView('scan');
    setDiagnosisData(null);
  };

  const handleBackToResults = () => {
    setCurrentView('results');
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {currentView === 'scan' && (
        <MainScan 
          onScanComplete={handleScanComplete} 
          isOffline={isOffline}
          setIsOffline={setIsOffline}
        />
      )}
      {currentView === 'results' && diagnosisData && (
        <DiagnosisResults 
          data={diagnosisData}
          onViewSpectrogram={handleViewSpectrogram}
          onBackToScan={handleBackToScan}
          isOffline={isOffline}
        />
      )}
      {currentView === 'spectrogram' && diagnosisData && (
        <SpectrogramViewer 
          data={diagnosisData}
          onBack={handleBackToResults}
        />
      )}
    </div>
  );
}
