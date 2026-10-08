import httpx
import os
import subprocess
import json
import tempfile
from pathlib import Path
from typing import List, Callable, Optional
from app.ml.schemas import Transcript, Segment, Word
from app.core.config import config
from app.core.errors import AppError
import time

def convert_for_groq(input_audio: str) -> str:
    """Convert audio to 16 kHz mono MP3 at 48 kbps."""
    out_path = str(Path(input_audio).with_suffix('.mp3'))
    cmd = [
        "ffmpeg", "-y", "-i", input_audio,
        "-ac", "1", "-ar", "16000",
        "-b:a", "48k", out_path
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return out_path
    except subprocess.CalledProcessError:
        raise AppError("AUDIO_CONVERT", "Failed to prepare audio for transcription.", "transcribing")
    except FileNotFoundError:
        # ffmpeg not found
        raise AppError("SYSTEM_ERROR", "ffmpeg is not installed", "transcribing")

def chunk_audio(audio_path: str) -> List[dict]:
    """Split into ~10 minute chunks with 10s overlap."""
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)
    if file_size_mb < 24:
        return [{"path": audio_path, "offset": 0.0}]
        
    chunks = []
    chunk_length_s = 600
    overlap_s = 10
    
    # Get duration using ffprobe
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_path]
    try:
        duration_str = subprocess.check_output(cmd).decode().strip()
        duration = float(duration_str)
    except Exception:
        raise AppError("AUDIO_ERROR", "Failed to determine audio duration.", "transcribing")
        
    start = 0.0
    while start < duration:
        end = min(start + chunk_length_s, duration)
        out_chunk = str(Path(audio_path).parent / f"chunk_{len(chunks)}.mp3")
        
        # Extract chunk
        split_cmd = [
            "ffmpeg", "-y", "-i", audio_path,
            "-ss", str(start), "-t", str(end - start),
            "-c", "copy", out_chunk
        ]
        subprocess.run(split_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        chunks.append({"path": out_chunk, "offset": start})
        
        if end >= duration:
            break
        start = end - overlap_s
        
    return chunks

class GroqTranscriber:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise AppError("ASR_AUTH", "Speech-to-text service is not configured correctly.", "transcribing")
        self.model = config.asr.model if config.asr.model else "whisper-large-v3"
        
    def transcribe(self, audio_path: str, glossary: list = None, on_segment: Callable = None, job=None) -> Transcript:
        mp3_path = convert_for_groq(audio_path)
        chunks = chunk_audio(mp3_path)
        
        initial_prompt = ""
        if glossary:
            initial_prompt = f"Glossary: {', '.join(glossary[:200])}."
            # keep under 224 tokens roughly
            if len(initial_prompt) > 800:
                initial_prompt = initial_prompt[:800]
                
        all_segments = []
        duration = 0.0
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        with httpx.Client(timeout=300.0) as client:
            for i, chunk in enumerate(chunks):
                if job:
                    # Update progress between 10 and 50 percent
                    progress = 10 + int(40 * (i / len(chunks)))
                    job.update(percent=progress)
                    
                chunk_file = chunk["path"]
                offset = chunk["offset"]
                
                with open(chunk_file, "rb") as f:
                    files = {"file": (Path(chunk_file).name, f, "audio/mpeg")}
                    data = {
                        "model": self.model,
                        "temperature": "0",
                        "response_format": "verbose_json",
                        "language": "en",
                        "timestamp_granularities[]": ["word", "segment"]
                    }
                    if initial_prompt:
                        data["prompt"] = initial_prompt
                        
                    retries = 3
                    while retries > 0:
                        try:
                            # throttle to stay under 20 requests per minute (max 1 req / 3 sec)
                            time.sleep(3) 
                            
                            resp = client.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=headers, files=files, data=data)
                            
                            if resp.status_code == 401:
                                raise AppError("ASR_AUTH", "Speech-to-text service is not configured correctly.", "transcribing")
                            elif resp.status_code == 429:
                                retry_after = int(resp.headers.get("retry-after", "10"))
                                time.sleep(retry_after)
                                retries -= 1
                                if retries == 0:
                                    raise AppError("ASR_RATE_LIMITED", "The speech-to-text service is busy. Please try again in a few minutes.", "transcribing")
                                continue
                            elif resp.status_code != 200:
                                raise AppError("ASR_UNAVAILABLE", f"Groq API error: {resp.status_code} {resp.text}", "transcribing")
                                
                            result = resp.json()
                            break
                        except httpx.RequestError:
                            retries -= 1
                            if retries == 0:
                                raise AppError("ASR_UNAVAILABLE", "Network or timeout error while contacting speech-to-text service.", "transcribing")
                            time.sleep(2)
                            
                duration = max(duration, offset + result.get("duration", 0.0))
                
                # Merge segments
                for s in result.get("segments", []):
                    seg_start = s["start"] + offset
                    seg_end = s["end"] + offset
                    
                    # deduplicate in overlap
                    # if this segment's midpoint falls in the overlap of the previous chunk, skip it
                    midpoint = (seg_start + seg_end) / 2
                    if offset > 0 and midpoint < offset + 5: # 10s overlap, midpoint in first 5s of chunk is in overlap
                        continue
                        
                    words = []
                    for w in s.get("words", []):
                        words.append(Word(
                            w=w["word"],
                            start=w["start"] + offset,
                            end=w["end"] + offset,
                            prob=None
                        ))
                    
                    # avg_logprob and no_speech_prob
                    avg_logprob = s.get("avg_logprob", 0.0)
                    
                    seg_obj = Segment(
                        id=0, # will renumber later
                        start=seg_start,
                        end=seg_end,
                        text=s["text"],
                        speaker_id="SPEAKER_00",
                        speaker_name=None,
                        overlap=False,
                        avg_logprob=avg_logprob,
                        no_speech_prob=s.get("no_speech_prob", 0.0),
                        words=words
                    )
                    all_segments.append(seg_obj)
                    
                    if on_segment:
                        word_dicts = [{"word": w.w, "start": w.start, "end": w.end, "prob": w.prob} for w in words]
                        on_segment({"id": len(all_segments), "start": seg_start, "end": seg_end, "text": seg_obj.text, "words": word_dicts})
                        
        # Renumber
        for i, s in enumerate(all_segments):
            s.id = i + 1
            
        return Transcript(
            segments=all_segments,
            asr_model=f"groq/{self.model}",
            language="en",
            duration=duration,
            warnings=[]
        )
