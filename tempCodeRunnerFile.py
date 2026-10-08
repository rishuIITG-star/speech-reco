import requests
import time
import json
import os

BASE_URL = "http://localhost:8000/api"

def test_pipeline():
    # 1. Register a test user
    email = "test@example.com"
    password = "password123"
    
    print("Registering user...")
    res = requests.post(f"{BASE_URL}/auth/register", json={"email": email, "password": password, "name": "Test User"})
    if res.status_code == 400 and "already registered" in res.text:
        print("User already registered. Proceeding to login.")
    elif res.status_code != 200:
        print(f"Failed to register: {res.text}")
        
    print("Logging in...")
    res = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": password})
    if res.status_code != 200:
        print(f"Failed to login: {res.text}")
        return
        
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Upload file
    audio_path = "test_audio.wav"
    if not os.path.exists(audio_path):
        print("test_audio.wav not found!")
        return
        
    print("Uploading file...")
    with open(audio_path, "rb") as f:
        files = {"file": f}
        data = {"title": "Test Meeting"}
        res = requests.post(f"{BASE_URL}/process", headers=headers, files=files, data=data)
        
    if res.status_code != 202:
        print(f"Failed to upload: {res.text}")
        return
        
    job_id = res.json()["job_id"]
    print(f"Job ID: {job_id}")
    
    # 3. Poll for status
    while True:
        res = requests.get(f"{BASE_URL}/status/{job_id}", headers=headers)
        if res.status_code != 200:
            print(f"Failed to get status: {res.text}")
            break
            
        status = res.json()
        state = status.get("state")
        progress = status.get("progress")
        current_step = status.get("current_step")
        
        print(f"Status: {state}, Progress: {progress}%, Step: {current_step}")
        
        if state == "completed":
            print("Pipeline completed successfully!")
            break
        elif state == "failed":