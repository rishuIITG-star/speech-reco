# 🎙️ Granola AI: Meeting Intelligence

An advanced, AI-powered meeting assistant designed to transcribe, refine, and extract actionable intelligence from audio recordings. The platform features state-of-the-art Automatic Speech Recognition (ASR), speaker diarization, and LLM-powered extraction to generate professional meeting minutes, agreed decisions, and action items—complete with verbatim audio evidence timestamps.

---

## ✨ Features

- **High-Accuracy Transcription**: Leverages `faster-whisper` or cloud-based `Groq` APIs for rapid, high-quality audio transcription.
- **Speaker Diarization**: Uses `pyannote.audio` to distinguish between speakers and map conversations accurately.
- **AI Refinement & Intelligence**: Uses Gemini/LLM providers to generate intelligent summaries, structural meeting minutes, and explicit action items.
- **Consensus Verification**: Extracts agreed-upon decisions and disputed proposals with direct timestamped evidence from the audio.
- **Interactive Web Interface**: A stunning React frontend featuring `framer-motion` animations, dynamic waveform visualization (`wavesurfer.js`), and instant progress streaming.
- **Secure Authentication**: JWT-based user authentication and data isolation using SQLite/SQLAlchemy.

---

## 🛠️ Technology Stack

### Backend (FastAPI / Python)
- **Framework**: FastAPI
- **Database**: SQLite via SQLAlchemy ORM
- **AI Models**: `faster-whisper`, `pyannote.audio`, Groq API, Gemini API
- **Streaming**: Server-Sent Events (SSE) for real-time transcription status
- **Testing**: `pytest`

### Frontend (React / Vite)
- **Framework**: React 19 + TypeScript + Vite
- **Routing**: React Router v7
- **Styling**: Tailwind CSS v4
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Audio Visualization**: Wavesurfer.js

---

## 🚀 Quick Start Guide

### Prerequisites
- Node.js (v18+)
- Python (v3.10+)
- Valid API keys (Groq, Gemini, HuggingFace for Diarization)

### 1. Environment Setup
In the `backend` folder, create a `.env` file based on `.env.example` (or configure the existing one):
```env
ASR_ENGINE=groq
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
HF_TOKEN=your_huggingface_token
DIARIZATION_ENABLED=false
REFINER_MODEL=gemini-3.5-flash
EXTRACTOR_MODEL=gemini-3.6-flash
ALLOWED_ORIGINS=http://localhost:5173
```

### 2. Run the Backend
Open a terminal, navigate to the `backend` directory, and start the FastAPI server:
```bash
cd backend

# Install dependencies (assuming virtual environment is active)
pip install -r requirements.txt

# Set Python path and run the server
$env:PYTHONPATH="."  # (On Windows PowerShell)
python app/main.py
```
*The backend will run on `http://localhost:8000`*

### 3. Run the Frontend
Open a new terminal, navigate to the `frontend` directory, and start the Vite dev server:
```bash
cd frontend
npm install
npm run dev
```
*The frontend will run on `http://localhost:5173`*

---

## 📂 Project Structure

```text
speech_reco/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI Routes (Auth, History, Upload)
│   │   ├── core/         # DB Models, Config, JWT Auth, Workers
│   │   └── ml/           # Machine Learning Pipelines (ASR, Extraction)
│   └── tests/            # Pytest test suite
├── frontend/
│   ├── src/
│   │   ├── components/   # React UI Components (Dashboard, Upload, Meeting, Results)
│   │   └── index.css     # Global Tailwind styles
│   ├── package.json      # Frontend dependencies
│   └── vite.config.ts    # Vite bundler config with API proxies
└── README.md
```

---

## 🧪 Running Tests
To run the backend integration and unit tests:
```bash
cd backend
$env:PYTHONPATH="."
pytest
```
