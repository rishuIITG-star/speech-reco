import sys
import argparse
from pathlib import Path
from app.ml.asr.validate import validate_audio
from app.ml.asr.normalize import normalize_audio
from app.ml.asr.transcribe import transcribe_audio
from app.ml.asr.postfilter import postfilter

def run(audio_path: str, glossary: list = None):
    input_path = Path(audio_path)
    validate_audio(input_path)
    
    norm_path = input_path.with_suffix(".norm.wav")
    normalize_audio(input_path, norm_path)
    
    transcript = transcribe_audio(str(norm_path), glossary)
    transcript = postfilter(transcript)
    
    print(transcript.model_dump_json(indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("audio", help="Path to audio file")
    parser.add_argument("--glossary", help="Comma separated list of terms")
    args = parser.parse_args()
    
    glossary_list = args.glossary.split(",") if args.glossary else None
    run(args.audio, glossary_list)
