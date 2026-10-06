import json
from pathlib import Path
from app.ml.schemas import Transcript, RefinedTranscript, RefinedSegment, Edit
from app.ml.llm.gemini import GeminiLLM
from app.ml.llm.ollama import OllamaLLM
from app.core.config import config
from app.ml.refine.candidates import get_candidates
from app.ml.refine.guards import validate_segment

def refine(transcript: Transcript, glossary: list = None) -> RefinedTranscript:
    if config.refiner.provider == "gemini":
        llm = GeminiLLM(
            model=config.refiner.model,
            temperature=config.refiner.temperature,
            fallbacks=["gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
        )
    else:
        llm = OllamaLLM(config.refiner.model, config.refiner.temperature)
    
    prompt_path = Path("prompts/refiner_system.txt")
    if prompt_path.exists():
        system_prompt = prompt_path.read_text(encoding="utf-8")
    else:
        system_prompt = "You correct speech-recognition errors in a meeting transcript. Output a JSON object with a 'segments' array. Each item must have 'id' (integer) and 'refined_text' (string)."
        
    system_prompt += "\n\nCRITICAL: Respond ONLY with valid JSON containing a 'segments' array. No markdown formatting, no backticks."
        
    candidates = get_candidates(transcript, glossary) if glossary else {}
    
    refined_segments = []
    
    # Chunking logic
    CHUNK_SIZE = 30
    segments_list = transcript.segments
    
    for i in range(0, len(segments_list), CHUNK_SIZE):
        chunk = segments_list[i:i + CHUNK_SIZE]
        
        user_prompt = f"Glossary: {glossary}\nCandidates: {candidates}\n\nSegments:\n"
        for seg in chunk:
            user_prompt += f"[{seg.id}] {seg.text}\n"
            
        try:
            response_text = llm.generate(system_prompt, user_prompt, response_format="json")
            response_data = json.loads(response_text)
            refined_data = response_data.get("segments", [])
            
            # Map LLM output
            refined_map = {item["id"]: item["refined_text"] for item in refined_data if "id" in item and "refined_text" in item}
            
            for seg in chunk:
                original = seg.text
                refined = refined_map.get(seg.id, None)
                
                if refined is None:
                    # Fallback if missing
                    refined_segments.append(RefinedSegment(id=seg.id, text=original, speaker=seg.speaker, start=seg.start, end=seg.end, changed=False))
                    continue
                    
                is_valid, reason = validate_segment(original, refined)
                if not is_valid:
                    print(f"Segment {seg.id} failed validation: {reason}. Falling back to raw.")
                    refined_segments.append(RefinedSegment(id=seg.id, text=original, speaker=seg.speaker, start=seg.start, end=seg.end, changed=False))
                else:
                    is_changed = original != refined
                    refined_segments.append(RefinedSegment(id=seg.id, text=refined, speaker=seg.speaker, start=seg.start, end=seg.end, changed=is_changed))
                    
        except Exception as e:
            from app.core.errors import AppError
            raise AppError("LLM_FAILED", str(e), "refining")
        
    return RefinedTranscript(
        segments=refined_segments,
        edits=[],
        refiner_model=llm.model,
        refiner_status="ok"
    )
