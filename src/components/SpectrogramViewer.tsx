import { useState } from 'react';
import { ArrowLeft, ZoomIn, ZoomOut, Maximize2, Play, Pause } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { DiagnosisData } from '../App';

interface SpectrogramViewerProps {
  data: DiagnosisData;
  onBack: () => void;
}

export function SpectrogramViewer({ data, onBack }: SpectrogramViewerProps) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [selectedTimeRange, setSelectedTimeRange] = useState<[number, number]>([0, data.vibrationData.length - 1]);
  const [isPlaying, setIsPlaying] = useState(false);
  const [viewMode, setViewMode] = useState<'amplitude' | 'frequency' | 'both'>('both');

  const handleZoomIn = () => {
    setZoomLevel((prev) => Math.min(prev + 0.5, 5));
  };

  const handleZoomOut = () => {
    setZoomLevel((prev) => Math.max(prev - 0.5, 1));
  };

  const handleResetZoom = () => {
    setZoomLevel(1);
    setSelectedTimeRange([0, data.vibrationData.length - 1]);
  };

  const getVisibleData = () => {
    const totalPoints = data.vibrationData.length;
    const pointsToShow = Math.floor(totalPoints / zoomLevel);
    const start = selectedTimeRange[0];
    const end = Math.min(start + pointsToShow, totalPoints);
    return data.vibrationData.slice(start, end);
  };

  const visibleData = getVisibleData();

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <button
              onClick={onBack}
              className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-6 h-6" />
            </button>
            <div>
              <h1 className="text-white mb-1">Analisis Spectrogram</h1>
              <p className="text-gray-400">
                Visualisasi data getaran mesin
              </p>
            </div>
          </div>

          {/* Zoom Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleZoomOut}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              disabled={zoomLevel <= 1}
            >
              <ZoomOut className="w-5 h-5" />
            </button>
            <span className="text-sm text-gray-300 min-w-[60px] text-center">
              {zoomLevel.toFixed(1)}x
            </span>
            <button
              onClick={handleZoomIn}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
              disabled={zoomLevel >= 5}
            >
              <ZoomIn className="w-5 h-5" />
            </button>
            <button
              onClick={handleResetZoom}
              className="p-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors ml-2"
            >
              <Maximize2 className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* View Mode Selector */}
        <div className="bg-gray-800 rounded-xl p-4 mb-6 flex items-center justify-between">
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('amplitude')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                viewMode === 'amplitude' ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              Amplitudo
            </button>
            <button
              onClick={() => setViewMode('frequency')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                viewMode === 'frequency' ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              Frekuensi
            </button>
            <button
              onClick={() => setViewMode('both')}
              className={`px-4 py-2 rounded-lg transition-colors ${
                viewMode === 'both' ? 'bg-red-600' : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              Keduanya
            </button>
          </div>

          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg transition-colors flex items-center gap-2"
          >
            {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isPlaying ? 'Jeda' : 'Putar'}</span>
          </button>
        </div>

        {/* Main Visualization */}
        <div className="bg-gray-800 rounded-xl p-6 backdrop-blur-sm mb-6">
          {(viewMode === 'amplitude' || viewMode === 'both') && (
            <div className="mb-8">
              <h3 className="text-white mb-4">Grafik Amplitudo Getaran</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={visibleData}>
                  <defs>
                    <linearGradient id="colorAmplitude" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#dc2626" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#dc2626" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="time" 
                    stroke="#9ca3af"
                    label={{ value: 'Waktu (detik)', position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
                  />
                  <YAxis 
                    stroke="#9ca3af"
                    label={{ value: 'Amplitudo', angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                    labelStyle={{ color: '#f3f4f6' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="amplitude" 
                    stroke="#dc2626" 
                    fillOpacity={1} 
                    fill="url(#colorAmplitude)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          )}

          {(viewMode === 'frequency' || viewMode === 'both') && (
            <div>
              <h3 className="text-white mb-4">Grafik Frekuensi Getaran</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={visibleData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis 
                    dataKey="time" 
                    stroke="#9ca3af"
                    label={{ value: 'Waktu (detik)', position: 'insideBottom', offset: -5, fill: '#9ca3af' }}
                  />
                  <YAxis 
                    stroke="#9ca3af"
                    label={{ value: 'Frekuensi (Hz)', angle: -90, position: 'insideLeft', fill: '#9ca3af' }}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '8px' }}
                    labelStyle={{ color: '#f3f4f6' }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="frequency" 
                    stroke="#dc2626" 
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        {/* Timeline Scrubber */}
        <div className="bg-gray-800 rounded-xl p-6 backdrop-blur-sm">
          <h3 className="text-white mb-4">Timeline Getaran</h3>
          <div className="relative">
            <ResponsiveContainer width="100%" height={100}>
              <AreaChart data={data.vibrationData}>
                <defs>
                  <linearGradient id="timelineGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#dc2626" stopOpacity={0.6}/>
                    <stop offset="95%" stopColor="#dc2626" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <Area 
                  type="monotone" 
                  dataKey="amplitude" 
                  stroke="#dc2626" 
                  fillOpacity={1} 
                  fill="url(#timelineGradient)" 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          
          {/* Timeline Info */}
          <div className="flex items-center justify-between mt-4 text-sm text-gray-400">
            <span>Durasi Total: {data.vibrationData[data.vibrationData.length - 1].time.toFixed(2)}s</span>
            <span>Data Points: {data.vibrationData.length}</span>
            <span>Sampling Rate: ~100 Hz</span>
          </div>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-gray-800 rounded-xl p-6 backdrop-blur-sm">
            <p className="text-gray-400 text-sm mb-2">Amplitudo Rata-rata</p>
            <p className="text-white text-2xl">
              {(visibleData.reduce((sum, d) => sum + d.amplitude, 0) / visibleData.length).toFixed(2)}
            </p>
          </div>
          
          <div className="bg-gray-800 rounded-xl p-6 backdrop-blur-sm">
            <p className="text-gray-400 text-sm mb-2">Frekuensi Dominan</p>
            <p className="text-white text-2xl">
              {Math.max(...visibleData.map(d => d.frequency)).toFixed(0)} Hz
            </p>
          </div>
          
          <div className="bg-gray-800 rounded-xl p-6 backdrop-blur-sm">
            <p className="text-gray-400 text-sm mb-2">Amplitudo Puncak</p>
            <p className="text-white text-2xl">
              {Math.max(...visibleData.map(d => d.amplitude)).toFixed(2)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}