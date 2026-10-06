from faster_whisper import WhisperModel
from app.core.config import config
from app.ml.schemas import Transcript, Segment, Word
import os
try:
    from pyannote.audio import Pipeline
except ImportError:
    Pipeline = None

model_instance = None
diarization_pipeline = None

def get_model():
    global model_instance, diarization_pipeline
    if model_instance is None:
        device = "cpu" if config.asr.device == "auto" else config.asr.device
        model_instance = WhisperModel(
            config.asr.model, 
            device=device, 
            compute_type=config.asr.compute_type_cpu
        )
        
    if diarization_pipeline is None and config.diarization.enabled and Pipeline and os.getenv("HF_TOKEN"):
        try:
            diarization_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=os.getenv("HF_TOKEN")
            )
            import torch
            if config.asr.device == "cuda" and torch.cuda.is_available():
                diarization_pipeline.to(torch.device("cuda"))
        except Exception as e:
            print(f"Failed to load Diarization pipeline: {e}")
            
    return model_instance, diarization_pipeline

def transcribe_audio(audio_path: str, glossary: list = None) -> Transcript:
    model, diarization_pipeline = get_model()
    
    initial_prompt = ""
    if glossary:
        initial_prompt = f"Glossary: {', '.join(glossary[:200])}."
        
    lang = config.asr.language if config.asr.language else None
        
    segments_gen, info = model.transcribe(
        audio_path,
        beam_size=config.asr.beam_size,
        language=lang,
        temperature=config.asr.temperature,
        condition_on_previous_text=False,
        compression_ratio_threshold=config.asr.compression_ratio_threshold,
        log_prob_threshold=config.asr.log_prob_threshold,
        no_speech_threshold=config.asr.no_speech_threshold,
        word_timestamps=True,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        initial_prompt=initial_prompt if initial_prompt else None
    )
    
    whisper_segments = list(segments_gen)
    
    # Run Pyannote Diarization
    diarization_result = None
    if diarization_pipeline:
        try:
            diarization_result = diarization_pipeline(audio_path)
        except Exception as e:
            print(f"Diarization failed: {e}")
            
    out_segments = []
    for i, s in enumerate(whisper_segments):
        words = []
        if s.words:
            for w in s.words:
                words.append(Word(w=w.word, start=w.start, end=w.end, prob=w.probability))
                
        # Map speaker using diarization
        speaker = "SPEAKER_00"
        if diarization_result:
            # find intersection
            overlap_max = 0.0
            best_speaker = "SPEAKER_00"
            for turn, _, spk in diarization_result.itertracks(yield_label=True):
                overlap = max(0, min(s.end, turn.end) - max(s.start, turn.start))
                if overlap > overlap_max:
                    overlap_max = overlap
                    best_speaker = spk
            if overlap_max > 0:
                speaker = best_speaker

        out_segments.append(Segment(
            id=i+1,
            start=s.start,
            end=s.end,
            text=s.text,
            speaker=speaker,
            avg_logprob=s.avg_logprob,
            no_speech_prob=s.no_speech_prob,
            words=words
        ))
        
    warnings = []
    if info.language_probability < 0.5:
        warnings.append(f"Low English probability: {info.language_probability:.2f}")
        
    return Transcript(
        segments=out_segments,
        asr_model=config.asr.model,
        language=info.language,
        duration=info.duration,
        warnings=warnings
    )
