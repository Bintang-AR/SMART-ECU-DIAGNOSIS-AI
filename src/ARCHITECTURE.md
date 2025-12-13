# Arsitektur Aplikasi Diagnostik Mesin

## 📐 Diagram Arsitektur

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER DEVICE                             │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              React Frontend (Browser)                     │ │
│  │                                                           │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ │ │
│  │  │  MainScan   │  │  Diagnosis   │  │  Spectrogram   │ │ │
│  │  │  Component  │  │  Results     │  │  Viewer        │ │ │
│  │  └──────┬──────┘  └──────────────┘  └─────────────────┘ │ │
│  │         │                                                │ │
│  │         ▼                                                │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │     MediaRecorder API (Browser Audio)           │   │ │
│  │  │     • Microphone Access                          │   │ │
│  │  │     • Audio Recording (webm format)              │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  │         │                                                │ │
│  │         ▼                                                │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │     API Service (/services/api.ts)              │   │ │
│  │  │     • analyzeAudio()                             │   │ │
│  │  │     • checkServerHealth()                        │   │ │
│  │  │     • saveOfflineRecording()                     │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  └───────────────────────────┬─────────────────────────────┘ │
│                              │                               │
└──────────────────────────────┼───────────────────────────────┘
                               │
                               │ HTTP/HTTPS
                               │ multipart/form-data
                               │
┌──────────────────────────────▼───────────────────────────────┐
│                     FastAPI Backend Server                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              API Endpoints                             │ │
│  │                                                        │ │
│  │  GET  /api/health     → Server health check          │ │
│  │  POST /api/analyze    → Audio analysis               │ │
│  │  GET  /api/history    → Get analysis history         │ │
│  └────────────────────────────────────────────────────────┘ │
│                              │                              │
│                              ▼                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          Audio Processing Pipeline                     │ │
│  │                                                        │ │
│  │  1. File Upload & Validation                          │ │
│  │     └─ Check file size, format, mode                  │ │
│  │                                                        │ │
│  │  2. Audio Preprocessing                               │ │
│  │     └─ Load audio with librosa                        │ │
│  │     └─ Resample to 44.1kHz                            │ │
│  │     └─ Normalize amplitude                            │ │
│  │                                                        │ │
│  │  3. Feature Extraction                                │ │
│  │     └─ MFCC (Mel-frequency cepstral coefficients)     │ │
│  │     └─ Spectral features (centroid, rolloff)          │ │
│  │     └─ Zero crossing rate                             │ │
│  │     └─ Chroma features                                │ │
│  │                                                        │ │
│  │  4. Model Inference                                   │ │
│  │     └─ Load pre-trained ML model                      │ │
│  │     └─ Run prediction                                 │ │
│  │     └─ Post-process results                           │ │
│  │                                                        │ │
│  │  5. Response Generation                               │ │
│  │     └─ Health score calculation                       │ │
│  │     └─ Issue detection & classification               │ │
│  │     └─ Recommendations generation                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                              │                              │
│                              ▼                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            ML Model (Your Trained Model)              │ │
│  │                                                        │ │
│  │  • TensorFlow / Keras Model (.h5)                    │ │
│  │  • PyTorch Model (.pt)                               │ │
│  │  • Scikit-learn Model (.pkl)                         │ │
│  │                                                        │ │
│  │  Input:  Audio features (MFCC, spectral, etc.)       │ │
│  │  Output: Health score + Issue classification         │ │
│  └────────────────────────────────────────────────────────┘ │
│                              │                              │
│                              ▼                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │          Database (Optional)                           │ │
│  │                                                        │ │
│  │  • PostgreSQL / MongoDB                               │ │
│  │  • Store analysis history                             │ │
│  │  • User data / Machine profiles                       │ │
│  │  • Audit logs                                         │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

## 🔄 Flow Diagram

### 1. Online Mode (Normal Operation)

```
User Click "Scan Mesin"
         │
         ▼
Request Microphone Permission
         │
         ▼
Start Recording (5s / 15s)
         │
         ▼
MediaRecorder captures audio
         │
         ▼
Stop Recording
         │
         ▼
Convert to Blob (webm format)
         │
         ▼
API Service: analyzeAudio()
         │
         ▼
POST /api/analyze
   ├─ file: audio.webm
   └─ mode: "quick" / "deep"
         │
         ▼
FastAPI Backend
   ├─ Validate request
   ├─ Load audio
   ├─ Extract features
   ├─ Run ML model
   └─ Generate response
         │
         ▼
Response JSON
   ├─ overall_health: 75
   ├─ issues: [...]
   └─ vibration_data: [...]
         │
         ▼
Update React State
         │
         ▼
Navigate to Results Page
         │
         ▼
Display Diagnosis Results
```

### 2. Offline Mode

```
User Toggle Offline Mode
         │
         ▼
User Click "Scan Mesin"
         │
         ▼
Start Recording
         │
         ▼
Stop Recording
         │
         ▼
Convert to Blob
         │
         ▼
saveOfflineRecording()
   └─ Save to localStorage
         │
         ▼
Generate Mock Data
   └─ Show preview results
         │
         ▼
User Toggle Online Mode
         │
         ▼
processOfflineRecordings()
   ├─ Load from localStorage
   ├─ For each recording:
   │   ├─ Send to FastAPI
   │   └─ Remove if successful
   └─ Keep failed ones
```

## 📊 Data Flow

### Request Data Structure

```typescript
// Frontend → Backend
FormData {
  file: Blob,          // Audio file (webm/wav)
  mode: "quick" | "deep"
}
```

### Response Data Structure

```typescript
// Backend → Frontend
interface FastAPIResponse {
  overall_health: number;        // 0-100
  issues: Array<{
    severity: "low" | "medium" | "high";
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
```

## 🔧 Component Responsibilities

### Frontend Components

#### 1. **MainScan.tsx**
- UI untuk scan controls
- Microphone access & recording
- Progress indicator
- Offline mode handling
- Call API service

#### 2. **DiagnosisResults.tsx**
- Display health score
- Show detected issues
- Recommendations
- Action buttons

#### 3. **SpectrogramViewer.tsx**
- Visualize vibration data
- Interactive timeline
- Zoom & pan features

#### 4. **API Service (/services/api.ts)**
- HTTP client for FastAPI
- Request/response handling
- Offline storage (localStorage)
- Error handling

### Backend Components

#### 1. **API Endpoints**
- `/api/health` - Health check
- `/api/analyze` - Main analysis
- `/api/history` - History retrieval

#### 2. **Audio Processing**
- File validation
- Audio loading (librosa)
- Feature extraction
- Noise reduction

#### 3. **ML Model**
- Load trained model
- Feature preprocessing
- Inference
- Result interpretation

#### 4. **Database (Optional)**
- Store analysis results
- User management
- Historical data

## 🔐 Security Considerations

### Frontend
- ✅ HTTPS only (production)
- ✅ Input validation
- ✅ Rate limiting awareness
- ✅ Secure localStorage usage

### Backend
- ✅ CORS configuration
- ✅ File size limits
- ✅ Content-Type validation
- ✅ Rate limiting (slowapi)
- ✅ Error handling
- ✅ Input sanitization
- ✅ Logging & monitoring

## 🚀 Deployment Options

### Frontend (React)
1. **Vercel** - Recommended for Next.js/React
2. **Netlify** - Easy static hosting
3. **AWS S3 + CloudFront** - Scalable CDN
4. **Firebase Hosting** - Google Cloud

### Backend (FastAPI)
1. **Railway** - Easy Python deployment
2. **Heroku** - Classic PaaS
3. **AWS EC2** - Full control
4. **Google Cloud Run** - Serverless containers
5. **DigitalOcean App Platform** - Simple & affordable

### Database
1. **Supabase** - PostgreSQL with APIs
2. **MongoDB Atlas** - Managed MongoDB
3. **AWS RDS** - Managed PostgreSQL
4. **Firebase Firestore** - NoSQL database

## 📈 Scaling Considerations

### Performance Optimization
- Use **Redis** for caching frequent requests
- Implement **background tasks** for long processing
- Use **message queue** (Celery + RabbitMQ) for async jobs
- **Load balancing** with multiple FastAPI instances
- **CDN** for static assets

### Monitoring
- **Sentry** for error tracking
- **Prometheus + Grafana** for metrics
- **New Relic** or **DataDog** for APM
- **CloudWatch** if using AWS

## 💾 Storage Requirements

### Audio Files
- Quick Scan: ~500KB per recording
- Deep Scan: ~1.5MB per recording
- Consider using **S3/Cloud Storage** if storing files long-term

### Model Files
- Typical ML model: 10-500MB
- Load once at startup
- Keep in memory for fast inference

### Database
- Start small: 1-2GB adequate for thousands of records
- Scale as needed based on usage

## 🧪 Testing Strategy

### Frontend
```bash
npm test                 # Unit tests
npm run test:e2e        # End-to-end tests
```

### Backend
```bash
pytest                  # All tests
pytest -v              # Verbose mode
pytest --cov           # With coverage
```

### Integration Testing
```python
# Test the full flow
import httpx

async def test_analyze_endpoint():
    async with httpx.AsyncClient() as client:
        with open("test_audio.webm", "rb") as f:
            response = await client.post(
                "http://localhost:8000/api/analyze",
                files={"file": f},
                data={"mode": "quick"}
            )
        assert response.status_code == 200
        assert "overall_health" in response.json()
```

## 📚 Next Steps

1. ✅ Setup FastAPI backend (see `backend_example.py`)
2. ✅ Train/prepare your ML model
3. ✅ Configure API_BASE_URL in frontend
4. ✅ Test locally
5. ✅ Deploy to production
6. 📊 Monitor performance
7. 🔄 Iterate based on feedback
