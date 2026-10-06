import pytest
from app.core.config import config, load_config
from app.core.errors import AppError, map_error_to_status
from app.core.jobs import create_job, JobStatus
from app.ml.schemas import ActionItem

def test_config_loaded():
    assert config.limits.max_upload_mb == 200
    assert config.asr.engine == "faster_whisper"
    assert config.extractor.provider == "gemini"

def test_errors():
    err = AppError("FILE_TOO_LARGE", "Too large", "validating")
    assert err.code == "FILE_TOO_LARGE"
    assert map_error_to_status("FILE_TOO_LARGE") == 413

def test_action_item_unspec():
    # Test normalization to 'unspecified'
    item = ActionItem(
        task="Do something",
        owner="none",
        deadline="TBD",
        timestamp=0.0,
        evidence="Some evidence",
        segment_ids=[1]
    )
    assert item.owner == "unspecified"
    assert item.deadline == "unspecified"
    
    item2 = ActionItem(
        task="Do it",
        owner="Marcus",
        deadline="Tomorrow",
        timestamp=0.0,
        evidence="Do it tomorrow",
        segment_ids=[2]
    )
    assert item2.owner == "Marcus"
    assert item2.deadline == "Tomorrow"

def test_jobs(tmp_path):
    job = JobStatus("test-123", jobs_dir=str(tmp_path))
    assert job.read()["state"] == "queued"
    
    job.update(state="running", percent=50)
    assert job.read()["state"] == "running"
    assert job.read()["percent"] == 50
    
    job.cancel()
    assert job.is_cancelled() is True
