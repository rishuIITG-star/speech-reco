import requests
import time
import os

BASE_URL = "http://localhost:8000/api"

def test_pipeline():
    audio_path = "test_audio.wav"
    if not os.path.exists(audio_path):
        print(f"{audio_path} not found!")
        return
        
    print("Uploading file WITHOUT token...")
    with open(audio_path, "rb") as f:
        files = {"file": f}
        data = {"title": "Test Meeting"}
        # Notice no headers={'Authorization': ...}
        res = requests.post(f"{BASE_URL}/process", files=files, data=data)
        
    if res.status_code != 202:
        print(f"Failed to upload: {res.text} (status: {res.status_code})")
        return
        
    job_id = res.json()["job_id"]
    print(f"Job ID: {job_id}")
    
    while True:
        res = requests.get(f"{BASE_URL}/status/{job_id}")
        if res.status_code != 200:
            print(f"Failed to get status: {res.text}")
            return
            
        status = res.json()
        print(f"Status: {status['state']} - {status['stage']} - {status['percent']}%")
        if status['state'] in ['done', 'failed']:
            print(f"Final status: {status}")
            break
        time.sleep(2)

if __name__ == "__main__":
    test_pipeline()
