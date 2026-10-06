from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import Optional
from pathlib import Path
import os
import json
from app.core.jobs import create_job, JobStatus
from app.core.worker import enqueue_job
from app.ml.pipeline import run_pipeline
from app.core.errors import map_error_to_status
from app.core.auth import get_current_user
from app.core.models import User, Meeting
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import Depends

router = APIRouter()

@router.post("/process")
async def process_audio(
    file: UploadFile = File(...),
    glossary: Optional[str] = Form(None),
    title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = create_job()
    
    input_ext = Path(file.filename).suffix if file.filename else ".webm"
    input_path = job.job_dir / f"input{input_ext}"
    
    with open(input_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    glossary_list = [g.strip() for g in glossary.split(",") if g.strip()] if glossary else None
    
    meeting = Meeting(
        job_id=job.job_id,
        user_id=current_user.id,
        title=title or file.filename or "Untitled Meeting",
        original_filename=file.filename,
        status="queued"
    )
    db.add(meeting)
    db.commit()
    
    enqueue_job(job, str(input_path), glossary_list)
    
    return JSONResponse(status_code=202, content={"job_id": job.job_id})

@router.get("/status/{job_id}")
def get_status(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.job_id == job_id, Meeting.user_id == current_user.id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    job = JobStatus(job_id)
    return job.read()

@router.get("/results/{job_id}")
def get_results(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.job_id == job_id, Meeting.user_id == current_user.id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    job = JobStatus(job_id)
    status = job.read()
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
        
    state = status.get("state")
    if state == "running" or state == "queued":
        return JSONResponse(status_code=409, content={"message": "Job still running"})
        
    if state == "failed":
        err_code = status["error"]["code"]
        return JSONResponse(status_code=map_error_to_status(err_code), content={"error": status["error"]})
        
    try:
        with open(job.job_dir / "transcript.json", "r", encoding="utf-8") as f:
            transcript = json.load(f)
        with open(job.job_dir / "refined.json", "r", encoding="utf-8") as f:
            refined = json.load(f)
        with open(job.job_dir / "record.json", "r", encoding="utf-8") as f:
            record = json.load(f)
        with open(job.job_dir / "minutes.md", "r", encoding="utf-8") as f:
            minutes_md = f.read()
            
        return {
            "transcript": transcript,
            "refined": refined,
            "record": record,
            "minutes_md": minutes_md
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error reading results")

@router.get("/audio/{job_id}")
def get_audio(job_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.job_id == job_id, Meeting.user_id == current_user.id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
        
    job = JobStatus(job_id)
    # Prefer normalized, fallback to input
    norm_path = job.job_dir / "norm.wav"
    if norm_path.exists():
        return FileResponse(norm_path, media_type="audio/wav")
        
    # Find input file
    for file in job.job_dir.glob("input.*"):
        return FileResponse(file)
        
    raise HTTPException(status_code=404, detail="Audio file not found")

@router.get("/history")
def get_history(limit: int = 20, offset: int = 0, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    meetings = db.query(Meeting).filter(Meeting.user_id == current_user.id).order_by(Meeting.created_at.desc()).offset(offset).limit(limit).all()
    return [{"id": m.id, "job_id": m.job_id, "title": m.title, "status": m.status, "created_at": m.created_at.isoformat(), "summary": m.summary[:200] + "..." if m.summary and len(m.summary) > 200 else m.summary} for m in meetings]

@router.get("/search")
def search_meetings(q: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not q or len(q.strip()) < 2:
        return []
    
    query_str = f"%{q}%"
    meetings = db.query(Meeting).filter(
        Meeting.user_id == current_user.id,
        or_(
            Meeting.title.ilike(query_str),
            Meeting.summary.ilike(query_str),
            Meeting.transcript_raw.ilike(query_str),
            Meeting.minutes_json.ilike(query_str)
        )
    ).order_by(Meeting.created_at.desc()).limit(20).all()
    
    return [{"id": m.id, "job_id": m.job_id, "title": m.title, "status": m.status, "created_at": m.created_at.isoformat(), "summary": m.summary[:200] + "..." if m.summary and len(m.summary) > 200 else m.summary} for m in meetings]

@router.get("/health")
def health():
    return {"status": "ok"}
