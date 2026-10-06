from typing import Literal, List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator

UNSPEC = "unspecified"
_EMPTY = {"", "none", "n/a", "na", "tbd", "unknown", "someone", "somebody", "team", "-"}

class _Unspec(BaseModel):
    @field_validator("owner", "deadline", mode="before", check_fields=False)
    @classmethod
    def _norm(cls, v):
        return UNSPEC if v is None or str(v).strip().lower() in _EMPTY else str(v).strip()

class Decision(BaseModel):
    text: str
    evidence: str
    segment_ids: List[int]
    timestamp: Optional[float] = None
    verified: bool = False

class ProposalNotAgreed(BaseModel):
    text: str
    evidence: str
    segment_ids: List[int]
    timestamp: Optional[float] = None
    verified: bool = False

class ActionItem(_Unspec):
    task: str
    owner: str = UNSPEC
    deadline: str = UNSPEC
    evidence: str
    segment_ids: List[int]
    timestamp: Optional[float] = None
    verified: bool = False

class MinutesTopic(BaseModel):
    title: str
    start: float
    end: float
    points: List[str]

class GroundingReport(BaseModel):
    kept: int
    dropped: List[dict] = []
    downgraded: List[dict] = []

class RecordMeta(BaseModel):
    job_id: str
    duration: float
    generated_at: str
    asr_model: str
    refiner_model: str
    extractor_model: str
    refiner_status: str
    warnings: List[str] = []
    grounding_report: GroundingReport

class MeetingRecord(BaseModel):
    summary: str
    minutes: List[MinutesTopic]
    decisions: List[Decision]
    proposals_not_agreed: List[ProposalNotAgreed]
    action_items: List[ActionItem]
    meta: RecordMeta

class Word(BaseModel):
    w: str
    start: float
    end: float
    prob: Optional[float] = None

class Segment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    avg_logprob: Optional[float] = None
    no_speech_prob: Optional[float] = None
    speaker: Optional[str] = None
    words: List[Word] = []

class Transcript(BaseModel):
    segments: List[Segment]
    asr_model: str
    language: str
    duration: float
    warnings: List[str] = []

class Edit(BaseModel):
    segment_id: int
    original: str
    corrected: str
    reason: str
    status: Literal["applied", "rejected"]
    reject_reason: Optional[str] = None

class RefinedSegment(BaseModel):
    id: int
    text: str
    speaker: Optional[str] = None
    start: Optional[float] = None
    end: Optional[float] = None
    changed: bool = False

class RefinedTranscript(BaseModel):
    segments: List[RefinedSegment]
    edits: List[Edit]
    refiner_model: str
    refiner_status: Literal["ok", "skipped"]
