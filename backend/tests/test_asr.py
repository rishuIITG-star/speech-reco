import pytest
from pathlib import Path
from app.core.errors import AppError
from app.ml.asr.validate import validate_audio
from app.ml.schemas import Transcript, Segment, Word
from app.ml.asr.postfilter import postfilter

def test_validate_audio_not_found():
    with pytest.raises(AppError) as exc:
        validate_audio(Path("does_not_exist.mp3"))
    assert exc.value.code == "UNSUPPORTED_FORMAT"

def test_postfilter():
    transcript = Transcript(
        segments=[
            Segment(id=1, start=0.0, end=1.0, text="Hello world", no_speech_prob=0.1, avg_logprob=-0.5),
            Segment(id=2, start=1.0, end=2.0, text="Thanks for watching", no_speech_prob=0.1, avg_logprob=-0.5),
            Segment(id=3, start=2.0, end=3.0, text="noise", no_speech_prob=0.9, avg_logprob=-1.5)
        ],
        asr_model="test",
        language="en",
        duration=3.0
    )
    
    filtered = postfilter(transcript)
    assert len(filtered.segments) == 1
    assert filtered.segments[0].text == "Hello world"
    assert filtered.segments[0].id == 1
