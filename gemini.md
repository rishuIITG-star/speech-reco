What the PS actually rewards
Criterion	Points	What decides it
Speech transcription	20	ASR model choice, audio prep, decoding settings
Transcript refinement	20	Fixing terms without changing meaning
Minutes and decisions	25	No invented or overstated decisions
Action items	15	Owner and deadline marked "unspecified" when not stated
End-to-end app	15	Works on unseen audio, clear errors
Submission quality	5	README, tech note, sample run

ASR is 20 points, but it also feeds everything downstream. Another 40 points depend on the LLM stages not hallucinating. So the plan puts depth into ASR, and it also adds a verification layer on the LLM outputs.

2. Architecture
Upload ─► Validate ─► Normalize (16 kHz mono) ─► VAD chunking
   ─► STT (Whisper) ─► RAW transcript (timestamps + confidence)
   ─► LLM-1 Refiner ─► REFINED transcript (+ change log)
   ─► LLM-2 Extractor ─► record.json (single source of truth)
   ─► minutes.md / .pdf  +  record.json   (both rendered from the same JSON)

Rendering both outputs from one JSON object guarantees the human-readable and machine-readable records say the same thing, which the PS requires.

Role	Suggested pick	Fallback
Speech-to-text	faster-whisper, Whisper large-v3 (int8_float16)	large-v3-turbo, distil-large-v3, or small.en
LLM-1 (refiner)	Qwen2.5-7B-Instruct or Llama 3.1 8B, local via Ollama, temperature 0	smaller local model
LLM-2 (extractor)	Gemini Flash-class model through a free AI Studio key (long context, JSON output)	a larger local model

Use different model families for the two LLMs so "separate language model" is unambiguous. Check which model versions are current before you commit. Run nvidia-smi to see your Lenovo LOQ's GPU and VRAM. An RTX card with 6 to 8 GB should run large-v3 in int8.

3. Speech-recognition framework (standalone module)

Build this as its own package, asr/, with one function: transcribe(path, glossary) -> Transcript. It has no web or LLM code, so you can test and benchmark it alone. Think of it as a kitchen prep line. Whisper is the chef, but it only cooks well if the ingredients are cleaned, portioned and seasoned first.

Step 1. Validate the file. Run ffprobe and reject with a specific error code for each case:

unsupported format
corrupt file
duration under about 1 second
silent audio (RMS energy near zero)
file too large

These map directly to the PS requirement for "clear error messages."

Step 2. Normalize the audio. Use ffmpeg to convert to 16 kHz, mono, PCM WAV, with loudness normalization (loudnorm). Whisper was trained on 16 kHz audio, so everything else is wasted resolution. Avoid aggressive denoising, because it often hurts Whisper more than it helps.

Step 3. Detect speech and chunk it. Use Silero VAD (built into faster-whisper via vad_filter=True). It cuts out silence and music, which are the main cause of hallucinated text. Whisper decodes in 30-second windows, so long meetings are processed as a sequence of windows. Use BatchedInferencePipeline if you need speed.

Step 4. Bias towards the domain. This is your edge. Add an optional "Meeting context" box in the UI where the user pastes expected terms, names and acronyms. Feed those into Whisper's hotwords and initial_prompt (the prompt is limited to roughly 220 tokens). The same glossary goes to LLM-1 later.

Step 5. Decode with safe settings.

python
segments, info = model.transcribe(
    wav, language="en", beam_size=5,
    vad_filter=True, vad_parameters=dict(min_silence_duration_ms=500),
    word_timestamps=True,
    condition_on_previous_text=False,   # stops repetition loops
    temperature=[0.0, 0.2, 0.4],        # retry hotter only if decoding fails
    compression_ratio_threshold=2.4,
    log_prob_threshold=-1.0,
    no_speech_threshold=0.6,
    hotwords=glossary_str, initial_prompt=prompt_str,
)

Step 6. Clean up the output.

Drop segments with repeated text or a high compression ratio.
Remove known silence hallucinations ("Thanks for watching" and similar).
Merge very short fragments.
Keep numbers in a consistent format.

Step 7. Save confidence data. Store each segment as {id, start, end, text, avg_logprob, no_speech_prob, words:[{w, start, end, prob}]}. This lets the UI highlight low-confidence words, and LLM-1 can use them as hints ("check these spans"). Few teams will do this, and it makes the raw-versus-refined comparison much more convincing.

Step 8. Speaker diarization (optional stretch). Use pyannote 3.1 (it needs a Hugging Face token) to get "Speaker 1/2" labels. Only add it if everything else is done. Speaker labels are not names, so an owner should still be marked "unspecified" unless a name is actually spoken.

Step 9. Benchmark it. Don't just claim large-v3 is better, show it:

Write 3 short mock-meeting scripts (5 to 8 minutes) with tricky content: acronyms, numbers, negations ("we will not ship"), a proposal that is never agreed, a task with no owner.
Record them yourselves. The script serves as ground truth for the transcript, and for the expected decisions and tasks.
Measure with jiwer, using Whisper's English text normalizer, and fill in this table:
Model	WER	Domain-term recall	Real-time factor	VRAM
small.en				
distil-large-v3				
large-v3				

Then measure WER again after refinement. That gives you evidence that LLM-1 helps and doesn't damage the text, and it goes straight into the technical description.

Step 10. Handle failures.

If the GPU runs out of memory, fall back to a smaller model or to CPU int8.
Add a timeout and per-chunk progress reporting.
Cache results by file hash so the demo is fast to re-run.
4. The two LLM stages

LLM-1, refiner. Send segment-aligned JSON (id to text) in chunks. It returns the same ids, with refined text and a change log (original, corrected, reason).

Guardrails to build in:

A programmatic check that numbers and negation words are unchanged unless the change was logged.
If a segment changes too much, fall back to the raw text for that segment.
The prompt says: fix only plausible recognition errors, never paraphrase, never add content.

LLM-2, extractor. For long meetings, extract per chunk, then merge and dedupe. The output schema is:

summary
minutes[]
decisions[], each with status: "agreed"
proposals_not_agreed[]
action_items[], each with task, owner, deadline, where owner and deadline default to "unspecified"

Every decision and task carries an evidence quote and timestamp. Code then checks that the quote really appears in the refined transcript, using fuzzy matching. It also forces owner and deadline back to "unspecified" if the name or date isn't in the quote. This directly protects the 40 points tied to minutes, decisions and tasks. Validate the JSON with Pydantic and retry on bad output.

5. App and UI (Stitch)

Stack: FastAPI backend with background jobs and Server-Sent Events for live status. The frontend is the Stitch export (HTML and Tailwind) served by FastAPI, with a little JavaScript. Avoid Streamlit if design quality matters.

Screens to design in Stitch:

Upload, with a drag-and-drop zone, an optional glossary box and a Start button.
Processing, a 3-step stepper (Transcribing, Refining, Documenting) with per-step status and error states.
Results with tabs: Raw, Refined (with a diff toggle and low-confidence highlights), Minutes, Decisions, Action items. The action items table shows "Unspecified" as a distinct grey chip.
An audio player where clicking a timestamp jumps to that point.
A downloads panel: .txt and .srt for transcripts, .md or .pdf for the record, and .json.

Stitch prompt to start from: "Clean, modern web app for an AI meeting assistant. Upload screen with drag-and-drop audio, optional glossary text area, and a primary Start button. A results page with tabs for Raw transcript, Refined transcript, Minutes, Decisions and Action items. Include a three-step progress stepper and an error banner state. Light theme, one accent colour, generous spacing."

6. Antigravity workflow

Put this plan in a PLAN.md in the repo and let the agents work one module at a time: asr/, then llm/, then api/, then frontend/. Review every diff yourself, and ask for tests for each module. Keep API keys in .env and never commit them.

7. Things I'd add
A rights-free sample recording with its generated outputs. The PS requires it, and your mock meeting works.
A Dockerfile, requirements.txt, .env.example and a README that can be followed from scratch.
A Colab or hosted fallback in case your laptop fails during the demo.
A short "limitations" section in the tech note. Honest limits score better than silence.
8. Timeline (deadline 7 Oct, so 3 days)