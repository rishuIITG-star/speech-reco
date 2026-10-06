# Capability Matrix

| Phase | Feature | Status | Notes |
|---|---|---|---|
| 0 | Benchmark set (Track A / Track B) | Partial | `test_pipeline.py` exists, but lacks clean/noisy Track A distinction and TTS Track B set. |
| 0 | Contract tests for current endpoints | Missing | `test_api.py` exists but needs formal strict contract validation without ML pipeline side effects. |
| 1 | Canonical schema (Stable IDs, Speaker ID vs Name) | Partial | Schemas exist but lack explicit separation of speaker identity from diarization labels. |
| 1 | Extractor -> Grounder Evidence Loop | Partial | Fuzzy grounding exists, but semantic fallback and verification gate are incomplete. |
| 1 | Verifiable Confidence Formula | Missing | Confidence currently leans heavily on raw ASR/LLM scores rather than a hard deterministic formula. |
| 1 | Refinement Fidelity Gate | Missing | No strict deterministic checks on numbers, dates, negations to prevent hallucination. |
| 1 | Audio Guardrails (NO_SPEECH, silence) | Missing | Validation script exists, but lacks strict meaningful word counts or silence bounds. |
| 1 | Relative Date Resolution | Missing | No deterministic deadline resolution mechanism against meeting timestamps. |
| 2 | Persisted Job State Machine | Partial | Jobs have basic states but lack granular tracking (REFINING, EXTRACTING, etc.) and error codes. |
| 2 | Per-stage checkpoints & Resume | Missing | Pipeline is executed monolithically. No checkpoint caching or idempotent resume. |
| 2 | Standardized Error Codes | Missing | Errors are raised as raw exceptions rather than unified codes (e.g. `ASR_FAILED`). |
| 2 | Concurrent Job Limits (CPU/GPU) | Partial | Worker thread limits concurrency, but no separate tracking for GPU vs CPU loads. |
| 3 | SSE Endpoint (`/api/jobs/{id}/events`) | Missing | Polling is used currently. |
| 3 | Split ResultsScreen (Summary, Transcripts, etc.) | Partial | `ResultsScreen.tsx` exists but is highly monolithic. |
| 3 | Evidence Card & Review Workflow | Missing | Read-only UI; no review, approve, edit, or reject flows implemented. |
| 4 | StorageService / JobQueue Abstractions | Missing | Hardcoded to local SQLite and local filesystem currently. |
| 4 | PostgreSQL + Alembic Migrations | Missing | Only SQLite via SQLAlchemy is supported. |
| 5 | Auth & Per-User Ownership | Missing | Open system, no authentication layer or tenant isolation. |
| 5 | Confidential Mode / Ollama | Partial | Ollama integration exists, but no explicit "confidential toggle". |
| 5 | Structured Logs & Metrics | Missing | Basic print/logging; no structured JSON logs with request IDs or formal metric tracking. |
| 6 | Deployment Docs & docker-compose | Missing | Basic README exists, but lacks docker-compose and environment templates. |
| 6 | Cross-meeting search (FTS + Embeddings) | Missing | Only basic query search implemented on single SQLite db. |
