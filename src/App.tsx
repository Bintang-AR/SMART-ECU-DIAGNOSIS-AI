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

  const handleScanComplete = (data: DiagnosisData) => {
    setDiagnosisData(data);
    setCurrentView('results');
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
    <div className="min-h-screen bg-black">
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