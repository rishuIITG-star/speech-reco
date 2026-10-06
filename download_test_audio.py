import urllib.request
import os

def download_sample():
    # A short public domain conversational clip (approx 1 minute, 2 speakers)
    # Using a Wikipedia/Wikimedia Commons file or similar reliable source
    # We will use an archive.org clip for Apollo 11 conversation
    url = "https://archive.org/download/Apollo11Audio/11_02_10_13.mp3"
    target = "multi_speaker_test.mp3"
    
    if not os.path.exists(target):
        print(f"Downloading {url} to {target}...")
        try:
            urllib.request.urlretrieve(url, target)
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download: {e}")
    else:
        print(f"{target} already exists.")

if __name__ == "__main__":
    download_sample()
