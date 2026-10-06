# Speech Recognition & Meeting Intelligence Implementation Plan

This document outlines the step-by-step implementation workflow for the Meeting Intelligence application based on the architecture discussed in our notes. The project is broken down into four independent modules to be developed sequentially.

## 1. Architecture Overview
The system processes audio through a multi-stage pipeline:
`Upload ─► Validate ─► Normalize (16 kHz mono) ─► VAD chunking ─► STT (Whisper) ─► LLM-1 Refiner ─► LLM-2 Extractor ─► record.json`

## 2. Module Implementation Phases

### Phase 1: ASR Module (`asr/`)
*Standalone speech-to-text pipeline.*
- **Step 1:** Implement audio validation (format, size, duration, corruption) using `ffprobe`.
- **Step 2:** Normalize audio (16 kHz, mono, loudnorm) via `ffmpeg`.
- **Step 3:** Implement Voice Activity Detection (VAD) chunking using Silero VAD to strip silence.
- **Step 4:** Integrate `faster-whisper` (Whisper large-v3 int8) for decoding with safe settings, capturing timestamps and confidence scores.
- **Step 5:** Add glossary injection via Whisper's `hotwords` and `initial_prompt`.
- **Deliverables:** `transcribe(path, glossary) -> Transcript` function, benchmark script (jiwer), mock meeting audio tests.

### Phase 2: LLM Processing (`llm/`)
*Refinement and structured extraction pipeline.*
- **LLM-1 (Refiner):** 
  - Use local Qwen2.5-7B-Instruct or Llama 3.1 8B via Ollama.
  - Apply segment-aligned JSON processing.
  - Add programmatic guardrails (numbers/negations unchanged unless logged).
- **LLM-2 (Extractor):**
  - Use Gemini Flash-class model.
  - Extract structured JSON matching UI schema (`summary`, `minutes`, `decisions`, `action_items`).
  - Implement fuzzy matching to verify extracted quotes match the refined transcript.
- **Deliverables:** LLM prompt chains, validation via Pydantic, and extraction tests.

### Phase 3: API Backend (`api/`)
*Server to stitch components together.*
- **Framework:** FastAPI.
- **Endpoints:** 
  - File upload and validation endpoint.
  - Server-Sent Events (SSE) for live streaming progress status to the frontend.
  - JSON result delivery.
- **Deliverables:** Background job queue, file hashing/caching, SSE integration.

### Phase 4: Frontend (`frontend/`)
*Web UI. (Currently In Progress!)*
- **Stack:** Vite, React, Tailwind CSS.
- **Screens:**
  - Upload screen with drag-and-drop & glossary input.
  - 3-step live processing stepper.
  - Granola-styled results view with tabs (Raw, Refined, Minutes, Decisions, Action Items).
- **Deliverables:** Responsive React SPA integrated with the FastAPI backend.

## 3. Agent Workflow Instructions
- Develop one module at a time following the order above (`asr/`, `llm/`, `api/`, `frontend/`).
- Each module must be independently tested before proceeding.
- Review every diff and verify output quality against the expected mock data.
- API keys must remain strictly in `.env`.
