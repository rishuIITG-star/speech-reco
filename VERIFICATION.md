# Phase 5: Verification Checklist

## Guardrails & Error Handling
- [x] `NO_SPEECH` correctly triggered for audio with < 20 words or > 80% silence probability.
- [x] `INVALID_AUDIO` (or `SILENT_AUDIO` / `UNREADABLE_AUDIO` / `EMPTY_AUDIO`) correctly triggered for short/silent/corrupted files.
- [x] UI properly displays the specific error code and a "Upload New Audio" retry button.
- [x] UI never shows a hallucinated summary from an empty or failed transcript.

## LLM Grounding & Fallbacks
- [x] Refiner successfully processes chunks of 30 segments.
- [x] Refiner successfully falls back to raw text if IDs mismatch, numbers change, or negations change.
- [x] Extractor strictly uses "unspecified" for missing owners/deadlines.
- [x] Extractor successfully resolves relative deadlines using the provided meeting context date.
- [x] "Verified Source" badge appears on Action Items and Decisions whose evidence strictly matches the transcript.

## State Management & UI Polish
- [x] Single-worker queue sequentially processes multiple simultaneous uploads without crashing.
- [x] Job status survives backend restart (SQLite state sync).
- [x] Frontend strictly enforces file types and < 500MB sizes on upload.

## End-to-End Tests
- [x] Scenario 1: Multi-speaker valid meeting (Full pipeline success, all tabs populated).
- [x] Scenario 2: Silent audio (Fails early with `SILENT_AUDIO`).
- [x] Scenario 3: Noise-only audio (Fails with `NO_SPEECH`).
- [x] Scenario 4: 3-second short clip (Fails early with `EMPTY_AUDIO`).
- [x] Scenario 5: WebM recording from frontend (Successfully processes).
- [x] Scenario 6: Corrupted/text file (Fails with `UNREADABLE_AUDIO` or `UNSUPPORTED_FORMAT`).

### Requirement
- Must have two consecutive clean runs across the board.
