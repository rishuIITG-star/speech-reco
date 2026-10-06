import json
from pathlib import Path
from datetime import datetime
from app.ml.schemas import RefinedTranscript, MeetingRecord, RecordMeta, Decision, ProposalNotAgreed, ActionItem, MinutesTopic
from app.ml.llm.gemini import GeminiLLM
from app.core.config import config
from app.ml.extract.chunking import chunk_transcript
from app.ml.extract.grounding import ground_items

def extract_record(job_id: str, transcript: RefinedTranscript, asr_model: str) -> MeetingRecord:
    llm = GeminiLLM(
        model=config.extractor.model,
        temperature=config.extractor.temperature,
        fallbacks=["gemini-3.8-flash"],
        forbidden_models=[transcript.refiner_model] if transcript.refiner_model else []
    )
    
    prompt_path = Path("prompts/extractor_system.txt")
    if prompt_path.exists():
        system_prompt = prompt_path.read_text(encoding="utf-8")
    else:
        system_prompt = "You write a meeting record strictly from the transcript provided."
        
    # Simplified to whole transcript for now
    
    system_prompt += f"\n\nJSON Schema to output:\n{json.dumps(MeetingRecord.model_json_schema(), indent=2)}"
    
    current_date = datetime.utcnow().strftime("%Y-%m-%d")
    user_prompt = f"Meeting Date: {current_date}\n\nTranscript:\n"
    for seg in transcript.segments:
        user_prompt += f"[{seg.id} | 00:00] {seg.text}\n"
        
    try:
        response_text = llm.generate(system_prompt, user_prompt, response_format="json")
        data = json.loads(response_text)
    except Exception as e:
        from app.core.errors import AppError
        if "json" in str(e).lower() or "validation" in str(e).lower():
            raise AppError("SCHEMA_INVALID", f"Extractor produced invalid schema: {str(e)}", "extracting")
        raise AppError("LLM_FAILED", str(e), "extracting")
        
    # parse
    decisions = [Decision(**d) for d in data.get("decisions", [])]
    proposals = [ProposalNotAgreed(**p) for p in data.get("proposals_not_agreed", [])]
    actions = [ActionItem(**a) for a in data.get("action_items", [])]
    minutes = [MinutesTopic(**m) for m in data.get("minutes", [])]
    
    items = {
        "summary": data.get("summary", ""),
        "minutes": minutes,
        "decisions": decisions,
        "proposals_not_agreed": proposals,
        "action_items": actions
    }
    
    grounded_items, report = ground_items(items, transcript.segments)
    
    meta = RecordMeta(
        job_id=job_id,
        duration=0.0,
        generated_at=datetime.utcnow().isoformat(),
        asr_model=asr_model,
        refiner_model=f"{config.refiner.provider}/{transcript.refiner_model}",
        extractor_model=f"{config.extractor.provider}/{llm.model}",
        refiner_status=transcript.refiner_status,
        grounding_report=report
    )
    
    return MeetingRecord(
        summary=grounded_items["summary"],
        minutes=grounded_items["minutes"],
        decisions=grounded_items["decisions"],
        proposals_not_agreed=grounded_items["proposals_not_agreed"],
        action_items=grounded_items["action_items"],
        meta=meta
    )
