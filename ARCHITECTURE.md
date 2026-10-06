# System Architecture

## Current State (Phase 0)

```mermaid
graph TD
    %% Frontend Components
    subgraph Frontend [Frontend (React + Vite + Tailwind)]
        UI[User Interface]
        API_Client[API Client / Fetch]
        UI --> API_Client
    end

    %% Backend Components
    subgraph Backend [Backend (FastAPI + Python)]
        Router[FastAPI Router]
        DB[(SQLite Database)]
        Worker[Background Worker Thread]
        Storage[Local File System]
        
        %% ML Pipeline
        subgraph ML_Pipeline [ML Audio Processing Pipeline]
            Validate[Validation & Normalization]
            ASR[ASR: Faster-Whisper]
            Refiner[Refiner LLM]
            Extractor[Extractor LLM]
            Grounding[Fuzzy Grounding]
            Render[Renderer MD/CSV]
        end
    end

    %% Connections
    API_Client -- "HTTP Proxy (/api)" --> Router
    Router -- Read/Write --> DB
    Router -- Enqueue Job --> Worker
    Worker -- Execute --> ML_Pipeline
    
    %% Pipeline Flow
    Validate --> ASR
    ASR --> Refiner
    Refiner --> Extractor
    Extractor --> Grounding
    Grounding --> Render
```

## Phase 1 Modification Plan (Files to Change vs Leave Alone)

### 🔴 Files to Change (Phase 1 focus: Evidence-Linked Core)
* `backend/app/ml/schemas.py`: Add `speaker_id` vs `speaker_name`, strict Pydantic definitions, overlap flags, evidence fields.
* `backend/app/ml/extract/extractor.py`: Update to pass numbered segments to LLM and expect segment_ids + short quote.
* `backend/app/ml/extract/grounding.py`: Enhance to verify quotes exactly -> fuzzy -> semantic. Add `match_type` and `verified` boolean.
* `backend/app/ml/refine/guards.py` / `refiner.py`: Introduce Refinement Fidelity Gate (deterministic checks on numbers, dates, negations).
* `backend/app/ml/asr/validate.py`: Add strict NO_SPEECH guardrails (<20 words, silence, corrupt audio).
* `backend/app/ml/pipeline.py`: Wire new extraction/grounding fields; compute verifiable confidence label (High/Medium/Review).
* `backend/tests/`: Substantial additions for unit-testing fidelity gates and date resolution.

### 🟢 Files to Leave Alone (For now)
* `frontend/`: Real-time UX, SSE, and Evidence cards are Phase 3.
* `backend/app/core/database.py`: PostgreSQL abstractions are Phase 4.
* `backend/app/api/`: SSE endpoints are Phase 3.
* `backend/app/core/auth.py` (if any): Security is Phase 5.
