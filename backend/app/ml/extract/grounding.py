from rapidfuzz import fuzz
from app.core.config import config
from app.ml.schemas import ActionItem, Decision, ProposalNotAgreed, GroundingReport, UNSPEC
import re

def fuzzy_match(evidence: str, window_text: str) -> bool:
    score = fuzz.partial_ratio(evidence.lower(), window_text.lower())
    return score >= config.grounding.evidence_min_ratio

def check_owner_deadline(item: ActionItem, window_text: str) -> list[dict]:
    downgrades = []
    window_lower = window_text.lower()
    
    # Check speaker label pattern
    speaker_pattern = re.compile(r"^speaker\s*[-_]?\s*\d+$", re.IGNORECASE)
    
    if item.owner != UNSPEC:
        if item.owner.lower() not in window_lower or speaker_pattern.match(item.owner):
            downgrades.append({"kind": "action_item", "field": "owner", "text": item.task})
            item.owner = UNSPEC
            
    if item.deadline != UNSPEC and item.deadline.lower() not in window_lower:
        downgrades.append({"kind": "action_item", "field": "deadline", "text": item.task})
        item.deadline = UNSPEC
        
    return downgrades

def get_window_text(segment_ids: list[int], seg_map: dict) -> str:
    window_sids = set()
    for sid in segment_ids:
        window_sids.update([sid - 1, sid, sid + 1])
    valid_sids = sorted([sid for sid in window_sids if sid in seg_map])
    return " ".join([seg_map[sid].text for sid in valid_sids])

def is_hedging(evidence: str) -> bool:
    hedges = ["should we", "maybe", "what if", "could we", "?"]
    agreements = ["agreed", "approved", "let's go with", "we'll", "we will", "sounds good", "okay", "yes"]
    
    ev = evidence.lower()
    has_hedge = any(h in ev for h in hedges)
    has_agree = any(a in ev for a in agreements)
    
    return has_hedge and not has_agree

def ground_items(items: dict, segments: list) -> tuple[dict, GroundingReport]:
    report = GroundingReport(kept=0)
    
    seg_map = {s.id: s for s in segments}
    
    out_decisions = []
    out_proposals = items.get("proposals_not_agreed", [])
    out_actions = []
    
    # Process decisions
    for d in items.get("decisions", []):
        window_text = get_window_text(d.segment_ids, seg_map)
        valid_sids = [sid for sid in d.segment_ids if sid in seg_map]
        d.timestamp = seg_map[valid_sids[0]].start if valid_sids else 0.0
        
        if not fuzzy_match(d.evidence, window_text):
            report.dropped.append({"kind": "decision", "text": d.text, "reason": "evidence_mismatch"})
            continue
            
        if is_hedging(d.evidence):
            out_proposals.append(ProposalNotAgreed(
                text=d.text, evidence=d.evidence, segment_ids=d.segment_ids, timestamp=d.timestamp, verified=True
            ))
            report.downgraded.append({"kind": "decision", "field": "type", "text": d.text})
            continue
            
        d.verified = True
        out_decisions.append(d)
        report.kept += 1
        
    # Process actions
    for a in items.get("action_items", []):
        window_text = get_window_text(a.segment_ids, seg_map)
        valid_sids = [sid for sid in a.segment_ids if sid in seg_map]
        a.timestamp = seg_map[valid_sids[0]].start if valid_sids else 0.0
        
        if not fuzzy_match(a.evidence, window_text):
            report.dropped.append({"kind": "action_item", "text": a.task, "reason": "evidence_mismatch"})
            continue
            
        downgrades = check_owner_deadline(a, window_text)
        report.downgraded.extend(downgrades)
            
        a.verified = True
        out_actions.append(a)
        report.kept += 1
        
    # Process proposals
    final_proposals = []
    for p in out_proposals:
        window_text = get_window_text(p.segment_ids, seg_map)
        valid_sids = [sid for sid in p.segment_ids if sid in seg_map]
        p.timestamp = seg_map[valid_sids[0]].start if valid_sids else 0.0
            
        if fuzzy_match(p.evidence, window_text):
            p.verified = True
            report.kept += 1
            final_proposals.append(p)
        else:
            report.dropped.append({"kind": "proposal", "text": p.text, "reason": "evidence_mismatch"})
            
    return {
        "summary": items.get("summary", ""),
        "minutes": items.get("minutes", []),
        "decisions": out_decisions,
        "proposals_not_agreed": final_proposals,
        "action_items": out_actions
    }, report
