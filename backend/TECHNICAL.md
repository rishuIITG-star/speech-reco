# TECHNICAL.md

## Models and Roles
- **ASR**: `faster-whisper` (large-v3 by default). Transcribes audio.
- **LLM-1 (Refiner)**: `qwen2.5:7b-instruct` via Ollama. Replaces misheard terms with glossary candidates.
- **LLM-2 (Extractor)**: `gemini-1.5-flash` via Gemini API. Extracts meeting records strictly from the refined transcript.

## Data Flow
Upload -> Validated -> Normalized (ffmpeg) -> Transcribed (faster-whisper) -> Refined (LLM-1 + Guards) -> Extracted (LLM-2 + Grounding) -> Rendered (Markdown/CSV).

## Guards
- **Refinement Guards**: Edits are rejected if they change numbers, negations, or commitments (modals).
- **Grounding Guards**: Extracted action items and decisions are checked against the transcript text using fuzzy matching. Unmatched items are dropped. Missing owners/deadlines are downgraded to "unspecified".

## Limitations
- ASR on CPU is slow; a CUDA GPU is recommended.
- Extraction relies on explicit agreement for decisions.
