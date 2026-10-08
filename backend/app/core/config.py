import yaml
import os
from pathlib import Path
from pydantic import BaseModel
from typing import List, Union
from dotenv import load_dotenv

load_dotenv()

class LimitsConfig(BaseModel):
    max_upload_mb: int
    min_duration_s: float
    max_duration_s: float
    silence_mean_db: float

class ASRConfig(BaseModel):
    engine: str
    model: str
    fallback_models: List[str]
    device: str
    compute_type_gpu: str
    compute_type_cpu: str
    beam_size: int
    temperature: List[float]
    compression_ratio_threshold: float
    log_prob_threshold: float
    no_speech_threshold: float
    language: str

class DiarizationConfig(BaseModel):
    enabled: bool

class LLMConfig(BaseModel):
    provider: str
    model: str
    temperature: float

class GroundingConfig(BaseModel):
    evidence_min_ratio: int
    max_evidence_segments: int

class AppConfig(BaseModel):
    limits: LimitsConfig
    asr: ASRConfig
    diarization: DiarizationConfig
    refiner: LLMConfig
    extractor: LLMConfig
    grounding: GroundingConfig

def load_config(config_path: str = "config.yaml") -> AppConfig:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    # Override with env variables if present
    if os.getenv("ASR_ENGINE"):
        data["asr"]["engine"] = os.getenv("ASR_ENGINE")
    
    if os.getenv("GROQ_STT_MODEL"):
        data["asr"]["model"] = os.getenv("GROQ_STT_MODEL")
    elif data["asr"]["engine"] == "groq" and data["asr"]["model"] not in ["whisper-large-v3"]:
        data["asr"]["model"] = "whisper-large-v3" # default for groq if not specified in config

    if data["asr"]["engine"] == "groq":
        data["diarization"]["enabled"] = False
        
    if os.getenv("DIARIZATION_ENABLED") is not None:
        val = os.getenv("DIARIZATION_ENABLED").lower()
        if data["asr"]["engine"] == "groq":
            data["diarization"]["enabled"] = False
        else:
            data["diarization"]["enabled"] = val in ["true", "1", "yes"]

    if os.getenv("MAX_UPLOAD_MB"):
        data["limits"]["max_upload_mb"] = int(os.getenv("MAX_UPLOAD_MB"))
    if os.getenv("MAX_DURATION_MIN"):
        data["limits"]["max_duration_s"] = float(os.getenv("MAX_DURATION_MIN")) * 60

    if os.getenv("REFINER_PROVIDER"):
        data["refiner"]["provider"] = os.getenv("REFINER_PROVIDER")
    if os.getenv("REFINER_MODEL"):
        data["refiner"]["model"] = os.getenv("REFINER_MODEL")
        
    if os.getenv("EXTRACTOR_PROVIDER"):
        data["extractor"]["provider"] = os.getenv("EXTRACTOR_PROVIDER")
    if os.getenv("EXTRACTOR_MODEL"):
        data["extractor"]["model"] = os.getenv("EXTRACTOR_MODEL")
        
    return AppConfig(**data)

# Global config instance loaded once
config = load_config()

# Read env variables securely
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")
JOBS_DIR = os.getenv("JOBS_DIR", "jobs")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./speech_reco.db")

