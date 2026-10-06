# Capability Matrix

| Phase | Feature | Status | Notes |
|---|---|---|---|
| 0 | Benchmark set (Track A / Track B) | Partial | `test_pipeline.py` exists, but lacks clean/noisy Track A distinction and TTS Track B set. |
| 0 | Contract tests for current endpoints | Missing | `test_api.py` exists but needs formal strict contract validation without ML pipeline side effects. |
| 1 | Canonical schema (Stable IDs, Speaker ID vs Name) | Completed | Schema has explicit segments/edits with ID linking and speaker tracking. |
| 1 | Extractor -> Grounder Evidence Loop | Completed | Extractor enforces segment IDs; grounder validates and extracts precise substrings. |
| 1 | Verifiable Confidence Formula | Completed | Refiner limits edits and grounder prevents unverified claims. |
| 1 | Refinement Fidelity Gate | Completed | Refiner uses patch approach with strict glossary and preservation guardrails. |
| 1 | Audio Guardrails (NO_SPEECH, silence) | Completed | Empty/silent files throw `AppError` caught gracefully by the pipeline. |
| 1 | Relative Date Resolution | Completed | Extractor LLM resolves dates to YYYY-MM-DD using meeting date context. |
| 2 | Persisted Job State Machine | Completed | Jobs use `status.json` with state, progress percent, error codes, and traces. |
| 2 | Per-stage checkpoints & Resume | Missing | Pipeline is executed monolithically. No checkpoint caching or idempotent resume. |
| 2 | Standardized Error Codes | Completed | Pipeline maps `AppError` to HTTP 4xx/5xx status codes gracefully. |
| 2 | Concurrent Job Limits (CPU/GPU) | Partial | Worker thread limits concurrency, but no separate tracking for GPU vs CPU loads. |
| 3 | SSE Endpoint (`/api/jobs/{id}/events`) | Completed | `GET /status/{job_id}/stream` yields SSE progress and transcribing segments. |
| 3 | Split ResultsScreen (Summary, Transcripts, etc.) | Completed | ResultsScreen is split with robust Framer Motion reveals. |
| 3 | Evidence Card & Review Workflow | Completed | ResultsScreen allows editing and saving verified Action Items and Decisions back to API. |
| 4 | StorageService / JobQueue Abstractions | Missing | Hardcoded to local SQLite and local filesystem currently. |
| 4 | PostgreSQL + Alembic Migrations | Missing | Only SQLite via SQLAlchemy is supported. |
| 5 | Auth & Per-User Ownership | Missing | Open system, no authentication layer or tenant isolation. |
| 5 | Confidential Mode / Ollama | Partial | Ollama integration exists, but no explicit "confidential toggle". |
| 5 | Structured Logs & Metrics | Missing | Basic print/logging; no structured JSON logs with request IDs or formal metric tracking. |
| 6 | Deployment Docs & docker-compose | Missing | Basic README exists, but lacks docker-compose and environment templates. |
| 6 | Cross-meeting search (FTS + Embeddings) | Missing | Only basic query search implemented on single SQLite db. |
