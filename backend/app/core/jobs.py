import json
import os
from pathlib import Path
import tempfile
import uuid
from typing import Optional
from datetime import datetime
from app.core.database import SessionLocal
from app.core.models import Meeting
from app.core.config import JOBS_DIR

class JobStatus:
    def __init__(self, job_id: str, jobs_dir: str = JOBS_DIR):
        self.job_id = job_id
        self.job_dir = Path(jobs_dir) / job_id
        self.status_file = self.job_dir / "status.json"
        
        self.job_dir.mkdir(parents=True, exist_ok=True)
        if not self.status_file.exists():
            self.write({
                "job_id": job_id,
                "state": "queued",
                "stage": "validating",
                "percent": 0,
                "message": "Waiting to start...",
                "error": None,
                "updated_at": datetime.utcnow().isoformat()
            })

    def read(self) -> dict:
        if not self.status_file.exists():
            return {}
        try:
            with open(self.status_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def write(self, data: dict):
        data["updated_at"] = datetime.utcnow().isoformat()
        
        # Write atomically
        fd, temp_path = tempfile.mkstemp(dir=str(self.job_dir))
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f)
        
        os.replace(temp_path, str(self.status_file))

    def update(self, **kwargs):
        data = self.read()
        data.update(kwargs)
        self.write(data)
        
        # Sync to DB
        try:
            db = SessionLocal()
            meeting = db.query(Meeting).filter(Meeting.job_id == self.job_id).first()
            if meeting:
                if "state" in kwargs:
                    meeting.status = kwargs["state"]
                if "stage" in kwargs:
                    meeting.stage = kwargs["stage"]
                if "percent" in kwargs:
                    meeting.percent = kwargs["percent"]
                if "message" in kwargs:
                    meeting.message = kwargs["message"]
                if "error" in kwargs:
                    meeting.error_json = json.dumps(kwargs["error"]) if kwargs["error"] else None
                db.commit()
            db.close()
        except Exception as e:
            print(f"Failed to sync job state to DB: {e}")
        
    def cancel(self):
        self.update(state="cancelled")
        
    def is_cancelled(self) -> bool:
        return self.read().get("state") == "cancelled"

def create_job() -> JobStatus:
    job_id = str(uuid.uuid4())
    return JobStatus(job_id)
