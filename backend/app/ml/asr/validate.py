import subprocess
import json
import os
from pathlib import Path
from app.core.errors import AppError
from app.core.config import config

def validate_audio(file_path: Path) -> float:
    if not file_path.exists():
        raise AppError("UNSUPPORTED_FORMAT", "File not found", "validating")
    
    size_mb = file_path.stat().st_size / (1024 * 1024)
    if size_mb > config.limits.max_upload_mb:
        raise AppError("FILE_TOO_LARGE", f"File exceeds {config.limits.max_upload_mb}MB", "validating")
    
    if size_mb == 0:
        raise AppError("EMPTY_AUDIO", "File is empty", "validating")

    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-select_streams", "a", "-of", "json", str(file_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
    except Exception:
        raise AppError("UNREADABLE_AUDIO", "Could not read audio stream or format", "validating")
        
    if "format" not in info or "duration" not in info["format"]:
        raise AppError("UNREADABLE_AUDIO", "Could not determine duration", "validating")
        
    duration = float(info["format"]["duration"])
    if duration < config.limits.min_duration_s:
        raise AppError("EMPTY_AUDIO", "Audio is too short", "validating")
        
    cmd_vol = [
        "ffmpeg", "-i", str(file_path), "-af", "volumedetect", "-vn", "-sn",
        "-f", "null", "NUL" if os.name == "nt" else "/dev/null"
    ]
    try:
        vol_result = subprocess.run(cmd_vol, capture_output=True, text=True)
        mean_volume = None
        for line in vol_result.stderr.splitlines():
            if "mean_volume" in line:
                parts = line.split(":")
                mean_volume = float(parts[1].strip().split(" ")[0])
                break
        
        if mean_volume is not None and mean_volume < config.limits.silence_mean_db:
            raise AppError("SILENT_AUDIO", "Audio appears to be completely silent", "validating")
    except Exception:
        pass 
        
    return duration
