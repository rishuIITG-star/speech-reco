from fastapi.testclient import TestClient
from app.main import app
from app.core.jobs import JobStatus
import json

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_status_not_found():
    response = client.get("/api/status/not-a-job")
    assert response.json() == {}

def test_results_not_found():
    response = client.get("/api/results/not-a-job")
    assert response.status_code == 404
