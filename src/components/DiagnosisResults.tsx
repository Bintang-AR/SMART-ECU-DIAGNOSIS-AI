import { AlertTriangle, CheckCircle, XCircle, Activity, ArrowLeft, Eye, Download, Share2 } from 'lucide-react';
import { DiagnosisData } from '../App';

interface DiagnosisResultsProps {
  data: DiagnosisData;
  onViewSpectrogram: () => void;
  onBackToScan: () => void;
  isOffline: boolean;
}

export function DiagnosisResults({ data, onViewSpectrogram, onBackToScan, isOffline }: DiagnosisResultsProps) {
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-gray-800 border-red-500 text-red-400';
      case 'medium':
        return 'bg-gray-800 border-amber-500 text-amber-400';
      case 'low':
        return 'bg-gray-800 border-blue-500 text-blue-400';
      default:
        return 'bg-gray-800 border-gray-600 text-gray-400';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <XCircle className="w-6 h-6 text-red-600" />;
      case 'medium':
        return <AlertTriangle className="w-6 h-6 text-amber-600" />;
      case 'low':
        return <CheckCircle className="w-6 h-6 text-blue-600" />;
      default:
        return <AlertTriangle className="w-6 h-6 text-gray-600" />;
    }
  };

  const getSeverityLabel = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'Kritis';
      case 'medium':
        return 'Perhatian';
      case 'low':
        return 'Info';
      default:
        return severity;
    }
  };

  const getHealthStatus = (health: number) => {
    if (health >= 80) return { label: 'Baik', color: 'text-green-600', bgColor: 'bg-green-500' };
    if (health >= 60) return { label: 'Cukup Baik', color: 'text-amber-600', bgColor: 'bg-amber-500' };
    return { label: 'Perlu Perhatian', color: 'text-red-600', bgColor: 'bg-red-500' };
  };

  const healthStatus = getHealthStatus(data.overallHealth);

  return (
    <div className="min-h-screen bg-black p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={onBackToScan}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-gray-300" />
          </button>
          <div className="flex-1">
            <h1 className="text-white">Hasil Diagnosis</h1>
            <p className="text-gray-400">
              {new Date(data.timestamp).toLocaleString('id-ID')} • {data.mode === 'quick' ? 'Quick Scan' : 'Deep Scan'}
            </p>
          </div>
        </div>

        {/* Overall Health Card */}
        <div className="bg-gray-800 rounded-2xl shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-white mb-1">Kesehatan Mesin</h2>
              <p className={`${healthStatus.color}`}>{healthStatus.label}</p>
            </div>
            <div className="text-right">
              <div className={`text-4xl ${healthStatus.color}`}>{data.overallHealth}%</div>
            </div>
          </div>
          
          {/* Health Bar */}
          <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`${healthStatus.bgColor} h-full transition-all duration-500 rounded-full`}
              style={{ width: `${data.overallHealth}%` }}
            />
          </div>
        </div>

        {/* Issues Cards */}
        <div className="space-y-4 mb-6">
          {data.issues.map((issue) => (
            <div
              key={issue.id}
              className={`bg-gray-800 rounded-xl shadow-md border-2 p-5 ${getSeverityColor(issue.severity)}`}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  {getSeverityIcon(issue.severity)}
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="text-white">{issue.component}</h3>
                    <span className="text-xs px-3 py-1 rounded-full bg-gray-900/50 text-gray-300">
                      {getSeverityLabel(issue.severity)}
                    </span>
                  </div>
                  <p className="text-gray-300 mb-3">{issue.description}</p>
                  <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-700">
                    <p className="text-sm text-gray-400">Rekomendasi:</p>
                    <p className="text-gray-200">{issue.recommendation}</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <button
            onClick={onViewSpectrogram}
            className="bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-md p-4 flex items-center justify-center gap-3 transition-colors"
          >
            <Activity className="w-5 h-5" />
            <span>Lihat Spectrogram</span>
          </button>
          
          <button
            onClick={() => alert('Fitur export akan segera hadir')}
            className="bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-md p-4 flex items-center justify-center gap-3 transition-colors"
          >
            <Download className="w-5 h-5" />
            <span>Unduh Laporan</span>
          </button>
          
          <button
            onClick={() => alert('Fitur share akan segera hadir')}
            className="bg-red-600 hover:bg-red-700 text-white rounded-xl shadow-md p-4 flex items-center justify-center gap-3 transition-colors"
          >
            <Share2 className="w-5 h-5" />
            <span>Bagikan</span>
          </button>
        </div>

        {/* Offline Notice */}
        {isOffline && (
          <div className="bg-amber-900 border border-amber-700 rounded-lg p-4 text-center">
            <p className="text-amber-200">
              Data disimpan secara lokal. Sinkronisasi akan dilakukan saat koneksi tersedia.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}