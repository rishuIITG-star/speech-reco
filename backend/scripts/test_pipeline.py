import requests
from pathlib import Path
import time
import json

BASE_URL = "http://localhost:8000/api"

def upload_and_wait(file_path: Path) -> dict:
    print(f"\n--- Testing {file_path.name} ---")
    
    with open(file_path, "rb") as f:
        res = requests.post(f"{BASE_URL}/process", files={"file": f})
        
    if res.status_code not in (200, 202):
        print(f"Failed to upload {file_path.name}: {res.status_code}")
        try:
            return res.json()
        except:
            return {"error": res.text}
            
    job_id = res.json()["job_id"]
    print(f"Job ID: {job_id}. Waiting for completion...")
    
    while True:
        status_res = requests.get(f"{BASE_URL}/status/{job_id}")
        if status_res.status_code != 200:
            print(f"Status check failed: {status_res.status_code}")
            return {"error": status_res.text}
            
        status = status_res.json()
        if status["state"] == "failed":
            print(f"Job failed as expected (or unexpectedly).")
            return status
            
        if status["state"] == "completed":
            print(f"Job completed.")
            return status
            
        time.sleep(2)

if __name__ == "__main__":
    audio_dir = Path("tests/audio")
    files_to_test = ["3_second.wav", "silent.wav", "noise.wav", "corrupted.wav"]
    
    for fname in files_to_test:
        fpath = audio_dir / fname
        if fpath.exists():
            result = upload_and_wait(fpath)
            if "error" in result:
                if isinstance(result["error"], dict):
                    print(f"Result: {result['error'].get('code')} - {result['error'].get('message')}")
                else:
                    print(f"Result: {result['error']}")
        else:
            print(f"File not found: {fname}")
