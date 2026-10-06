import subprocess
from pathlib import Path
from app.core.errors import AppError

def normalize_audio(input_path: Path, output_path: Path):
    cmd = [
        "ffmpeg", "-y", "-i", str(input_path),
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
        "-af", "dynaudnorm",
        str(output_path)
    ]
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        raise AppError("UNREADABLE_AUDIO", "Failed to normalize audio", "normalizing")
