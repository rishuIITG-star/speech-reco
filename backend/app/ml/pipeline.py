import threading
from pathlib import Path
import traceback
from app.core.jobs import JobStatus
from app.ml.asr.validate import validate_audio
from app.ml.asr.normalize import normalize_audio
from app.ml.asr.transcribe import transcribe_audio
from app.ml.asr.postfilter import postfilter
from app.ml.refine.refiner import refine
from app.ml.extract.extractor import extract_record
from app.ml.render.markdown import render_minutes
from app.ml.render.csv import render_action_items_csv
from app.core.database import SessionLocal
from app.core.models import Meeting
from app.core.errors import AppError
import json

pipeline_lock = threading.Lock()

def run_pipeline(job: JobStatus, input_path: str, glossary: list = None):
    with pipeline_lock:
        if job.is_cancelled():
            return
            
        try:
            input_file = Path(input_path)
            
            job.update(state="running", stage="validating", percent=0)
            validate_audio(input_file)
            
            job.update(stage="normalizing", percent=5)
            norm_file = job.job_dir / "normalized.wav"
            normalize_audio(input_file, norm_file)
            
            job.update(stage="transcribing", percent=10)
            
            stream_file = job.job_dir / "stream.jsonl"
            def on_seg(seg):
                with open(stream_file, "a", encoding="utf-8") as sf:
                    sf.write(json.dumps(seg) + "\n")
                    
            transcript = transcribe_audio(str(norm_file), glossary, on_segment=on_seg, job=job)
            transcript = postfilter(transcript)
            
            with open(job.job_dir / "transcript.json", "w", encoding="utf-8") as f:
                f.write(transcript.model_dump_json(indent=2))
                
            total_words = sum(len(s.text.split()) for s in transcript.segments)
            avg_no_speech_prob = sum(s.no_speech_prob for s in transcript.segments) / max(len(transcript.segments), 1)
            
            if total_words < 20:
                raise AppError("NO_SPEECH", f"Transcript too short (only {total_words} words). The audio may be silent or lack clear speech.", "transcribing")
            if avg_no_speech_prob > 0.8:
                raise AppError("NO_SPEECH", "High probability of no speech detected across segments.", "transcribing")
                
            job.update(stage="refining", percent=50)
            refined = refine(transcript, glossary)
            with open(job.job_dir / "refined.json", "w", encoding="utf-8") as f:
                f.write(refined.model_dump_json(indent=2))
                
            job.update(stage="extracting", percent=75)
            record = extract_record(job.job_id, refined, transcript.asr_model)
            with open(job.job_dir / "record.json", "w", encoding="utf-8") as f:
                f.write(record.model_dump_json(indent=2))
                
            job.update(stage="rendering", percent=95)
            minutes_md = render_minutes(record)
            with open(job.job_dir / "minutes.md", "w", encoding="utf-8") as f:
                f.write(minutes_md)
                
            actions_csv = render_action_items_csv(record)
            with open(job.job_dir / "action_items.csv", "w", encoding="utf-8") as f:
                f.write(actions_csv)
                
            job.update(state="done", stage="done", percent=100)
            
            with SessionLocal() as db:
                meeting = db.query(Meeting).filter(Meeting.job_id == job.job_id).first()
                if meeting:
                    meeting.status = "done"
                    meeting.summary = record.summary
                    meeting.transcript_raw = transcript.model_dump_json(indent=2)
                    meeting.transcript_refined = refined.model_dump_json(indent=2)
                    meeting.minutes_json = json.dumps({
                        "decisions": [d.model_dump() for d in record.decisions],
                        "action_items": [a.model_dump() for a in record.action_items],
                        "minutes": [m.model_dump() for m in record.minutes]
                    })
                    db.commit()
            
        except Exception as e:
            if isinstance(e, AppError):
                job.update(state="failed", error={"code": e.code, "message": e.message, "stage": e.stage})
            else:
                traceback.print_exc()
                job.update(state="failed", error={"code": "INTERNAL_ERROR", "message": str(e), "stage": job.read().get("stage", "unknown")})
                
            with SessionLocal() as db:
                meeting = db.query(Meeting).filter(Meeting.job_id == job.job_id).first()
                if meeting:
                    meeting.status = "failed"
                    db.commit()
