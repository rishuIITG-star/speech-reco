from typing import Optional

class AppError(Exception):
    """Base typed error for the application."""
    def __init__(self, code: str, message: str, stage: str):
        super().__init__(message)
        self.code = code
        self.message = message
        self.stage = stage

class AudioProcessingError(AppError):
    pass

class ExtractionError(AppError):
    pass

def map_error_to_status(code: str) -> int:
    mapping = {
        "UNSUPPORTED_FORMAT": 415,
        "FILE_TOO_LARGE": 413,
        "UNREADABLE_AUDIO": 422,
        "INVALID_AUDIO": 422,
        "EMPTY_AUDIO": 422,
        "SILENT_AUDIO": 422,
        "NO_SPEECH_DETECTED": 422,
        "NO_SPEECH": 422,
        "EXTRACTION_FAILED": 500,
        "ASR_FAILED": 500,
        "DIARIZATION_FAILED": 500,
        "LLM_FAILED": 500,
        "SCHEMA_INVALID": 500
    }
    return mapping.get(code, 500)
