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
            fallbacks=["gemini-3.8-flash"]
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
    all_edits = []
    
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
            edits_data = response_data.get("edits", [])
            
            # Map LLM output
            edits_by_seg = {}
            for e in edits_data:
                if "segment_id" in e and "original" in e and "corrected" in e:
                    sid = e["segment_id"]
                    if sid not in edits_by_seg:
                        edits_by_seg[sid] = []
                    edits_by_seg[sid].append(e)
            
            for seg in chunk:
                original = seg.text
                seg_edits = edits_by_seg.get(seg.id, [])
                
                if not seg_edits:
                    refined_segments.append(RefinedSegment(id=seg.id, text=original, speaker_id=seg.speaker_id, speaker_name=seg.speaker_name, overlap=seg.overlap, start=seg.start, end=seg.end, changed=False))
                    continue
                    
                refined = original
                applied_edits_for_seg = []
                for e in seg_edits:
                    if e["original"] in refined:
                        new_refined = refined.replace(e["original"], e["corrected"], 1)
                        is_valid, reason = validate_segment(original, new_refined, glossary)
                        
                        edit_obj = Edit(
                            segment_id=seg.id,
                            original=e["original"],
                            corrected=e["corrected"],
                            reason=e.get("reason", ""),
                            status="applied",
                            reject_reason=None
                        )
                        
                        if is_valid:
                            refined = new_refined
                            applied_edits_for_seg.append(edit_obj)
                            all_edits.append(edit_obj)
                        else:
                            edit_obj.status = "rejected"
                            edit_obj.reject_reason = reason
                            all_edits.append(edit_obj)
                            print(f"Edit on Segment {seg.id} rejected: {reason}")
                    else:
                        edit_obj = Edit(
                            segment_id=seg.id,
                            original=e["original"],
                            corrected=e["corrected"],
                            reason=e.get("reason", ""),
                            status="rejected",
                            reject_reason="Substring not found in text"
                        )
                        all_edits.append(edit_obj)
                
                is_changed = original != refined
                refined_segments.append(RefinedSegment(id=seg.id, text=refined, speaker_id=seg.speaker_id, speaker_name=seg.speaker_name, overlap=seg.overlap, start=seg.start, end=seg.end, changed=is_changed))
                    
        except Exception as e:
            from app.core.errors import AppError
            raise AppError("LLM_FAILED", str(e), "refining")
        
    return RefinedTranscript(
        segments=refined_segments,
        edits=all_edits,
        refiner_model=llm.model,
        refiner_status="ok"
    )
