import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.models import User, Meeting

# Mock Dependencies
def mock_get_current_user():
    return User(id=1, email="test@example.com")

from datetime import datetime

def mock_get_db():
    db = MagicMock()
    # Mock meeting query
    mock_meeting = Meeting(id=1, job_id="test-job-123", user_id=1, title="Test", status="completed", created_at=datetime.utcnow(), summary="A summary")
    db.query.return_value.filter.return_value.first.return_value = mock_meeting
    db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [mock_meeting]
    db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [mock_meeting]
    yield db

# Override app dependencies
app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[get_db] = mock_get_db

client = TestClient(app)

def test_health_contract():
    """Verify /health returns 200 OK and expected shape."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch("app.api.routes.create_job")
@patch("app.api.routes.enqueue_job")
def test_process_audio_contract(mock_enqueue, mock_create_job):
    """Verify POST /process accepts audio and returns a 202 with job_id."""
    mock_job = MagicMock()
    mock_job.job_id = "new-job-456"
    mock_job.job_dir = MagicMock()
    mock_create_job.return_value = mock_job
    
    # Send dummy file
    files = {"file": ("test.wav", b"dummy audio content", "audio/wav")}
    data = {"title": "Test Audio", "glossary": "term1, term2"}
    
    response = client.post("/api/process", files=files, data=data)
    assert response.status_code == 202
    assert "job_id" in response.json()
    assert response.json()["job_id"] == "new-job-456"

@patch("app.api.routes.JobStatus")
def test_status_contract(mock_job_status):
    """Verify GET /status/{job_id} returns the job state."""
    mock_instance = mock_job_status.return_value
    mock_instance.read.return_value = {"state": "running", "progress": 0.5}
    
    response = client.get("/api/status/test-job-123")
    assert response.status_code == 200
    assert response.json() == {"state": "running", "progress": 0.5}

@patch("app.api.routes.JobStatus")
@patch("builtins.open")
@patch("json.load")
def test_results_contract(mock_json_load, mock_open, mock_job_status):
    """Verify GET /results/{job_id} returns all expected artifact JSONs."""
    mock_instance = mock_job_status.return_value
    mock_instance.read.return_value = {"state": "done"}
    
    # Mock json.load to return a dummy dict
    mock_json_load.return_value = {"dummy": "data"}
    
    response = client.get("/api/results/test-job-123")
    assert response.status_code == 200
    
    data = response.json()
    assert "transcript" in data
    assert "refined" in data
    assert "record" in data
    assert "minutes_md" in data

def test_history_contract():
    """Verify GET /history returns a list of meetings."""
    response = client.get("/api/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "job_id" in data[0]
        assert "title" in data[0]
        assert "status" in data[0]

def test_search_contract():
    """Verify GET /search?q=... returns matching meetings."""
    response = client.get("/api/search?q=test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "job_id" in data[0]
        assert "title" in data[0]

@patch("app.api.routes.JobStatus")
@patch("builtins.open")
@patch("json.load")
@patch("json.dump")
def test_save_results_contract(mock_dump, mock_load, mock_open, mock_job_status):
    """Verify POST /results/{job_id}/save updates record and returns 200."""
    mock_instance = mock_job_status.return_value
    mock_instance.job_dir = MagicMock()
    mock_instance.job_dir.__truediv__.return_value.exists.return_value = True
    
    mock_load.return_value = {"action_items": [], "decisions": []}
    
    response = client.post("/api/results/test-job-123/save", json={"action_items": [{"task": "Edited"}], "decisions": []})
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
