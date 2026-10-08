import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uuid

from app.main import app
from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_speech_reco.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup():
    # Run before test
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Run after test

def test_register_and_login():
    res = client.post("/api/auth/register", json={"email": "test@example.com", "password": "password123"})
    assert res.status_code == 200
    
    res = client.post("/api/auth/login", data={"username": "test@example.com", "password": "password123"})
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_protected_routes():
    res = client.get("/api/history", headers={"Authorization": "Bearer badtoken"})
    assert res.status_code == 401

def test_ownership_isolation():
    # User 1
    client.post("/api/auth/register", json={"email": "u1@example.com", "password": "password123"})
    token1 = client.post("/api/auth/login", data={"username": "u1@example.com", "password": "password123"}).json()["access_token"]
    
    # User 2
    client.post("/api/auth/register", json={"email": "u2@example.com", "password": "password123"})
    token2 = client.post("/api/auth/login", data={"username": "u2@example.com", "password": "password123"}).json()["access_token"]
    
    # User 1 creates a meeting
    with open("test_audio.txt", "w") as f:
        f.write("fake audio")
    
    res = client.post(
        "/api/process",
        headers={"Authorization": f"Bearer {token1}"},
        files={"file": ("test_audio.txt", open("test_audio.txt", "rb"), "text/plain")}
    )
    assert res.status_code == 202
    job_id = res.json()["job_id"]
    
    # User 1 can view status
    res = client.get(f"/api/status/{job_id}", headers={"Authorization": f"Bearer {token1}"})
    assert res.status_code == 200
    
    # User 2 CANNOT view status
    res = client.get(f"/api/status/{job_id}", headers={"Authorization": f"Bearer {token2}"})
    assert res.status_code == 404
    
def test_search():
    client.post("/api/auth/register", json={"email": "u3@example.com", "password": "password123"})
    token = client.post("/api/auth/login", data={"username": "u3@example.com", "password": "password123"}).json()["access_token"]
    
    # Search when empty
    res = client.get("/api/search?q=test", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert len(res.json()) == 0
