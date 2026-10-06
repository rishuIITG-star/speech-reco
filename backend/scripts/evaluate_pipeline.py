import json
from pathlib import Path
from rapidfuzz import fuzz
from pydantic import BaseModel
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from app.ml.schemas import RefinedTranscript, RefinedSegment
from app.ml.extract.extractor import extract_record

THRESHOLDS = {
    "decision_precision": 70.0,
    "decision_recall": 70.0,
    "action_precision": 70.0,
    "action_recall": 70.0,
    "owner_accuracy": 70.0,
    "evidence_precision": 60.0,
    "evidence_recall": 60.0
}

def load_data(variant: str):
    data_dir = Path(f"benchmark_data/track_a/{variant}")
    meetings = []
    for gt_path in data_dir.glob("*_gt.json"):
        base = gt_path.name.replace("_gt.json", "")
        tx_path = data_dir / f"{base}_transcript.json"
        
        with open(gt_path) as f:
            gt = json.load(f)
        with open(tx_path) as f:
            tx = json.load(f)
            
        meetings.append({"id": base, "gt": gt, "tx": tx})
    return meetings

def match_items(pred_items, gt_items):
    tps = 0
    fp = 0
    fn = 0
    evidence_tp = 0
    evidence_fp = 0
    evidence_fn = 0
    owner_correct = 0
    
    gt_matched = set()
    
    for pred in pred_items:
        best_score = 0
        best_gt_idx = -1
        
        for i, gt in enumerate(gt_items):
            if i in gt_matched:
                continue
            pred_text = pred.get("text") or pred.get("task", "")
            gt_text = gt.get("text") or gt.get("task", "")
            score = fuzz.token_set_ratio(pred_text, gt_text)
            if score > best_score:
                best_score = score
                best_gt_idx = i
                
        if best_score > 70:
            tps += 1
            gt_matched.add(best_gt_idx)
            
            gt_item = gt_items[best_gt_idx]
            
            # Owner matching
            if "owner" in pred and "owner" in gt_item:
                if fuzz.ratio(str(pred["owner"]).lower(), str(gt_item["owner"]).lower()) > 80:
                    owner_correct += 1
            
            # Evidence matching
            pred_ev = set(pred.get("evidence_segment_ids", []))
            gt_ev = set(gt_item.get("evidence_segment_ids", []))
            
            evidence_tp += len(pred_ev.intersection(gt_ev))
            evidence_fp += len(pred_ev - gt_ev)
            evidence_fn += len(gt_ev - pred_ev)
        else:
            fp += 1
            evidence_fp += len(pred.get("evidence_segment_ids", []))
            
    fn = len(gt_items) - len(gt_matched)
    for i, gt in enumerate(gt_items):
        if i not in gt_matched:
            evidence_fn += len(gt.get("evidence_segment_ids", []))
            
    return tps, fp, fn, evidence_tp, evidence_fp, evidence_fn, owner_correct

def evaluate_variant(variant: str, f_out):
    meetings = load_data(variant)
    f_out.write(f"\n## Track A: {variant.upper()}\n")
    
    total_dec_tp = total_dec_fp = total_dec_fn = 0
    total_act_tp = total_act_fp = total_act_fn = 0
    total_ev_tp = total_ev_fp = total_ev_fn = 0
    total_owner = 0
    total_act_with_owner = 0
    
    for m in meetings:
        segments = [RefinedSegment(**s) for s in m["tx"]]
        transcript = RefinedTranscript(
            segments=segments, 
            edits=[],
            asr_model="mock",
            refiner_model="mock",
            refiner_status="skipped"
        )
        
        # Run extractor directly
        record = extract_record("job_mock", transcript, "mock")
        
        pred_dec = [d.model_dump() for d in record.decisions]
        gt_dec = m["gt"].get("decisions", [])
        dtp, dfp, dfn, ev_tp1, ev_fp1, ev_fn1, _ = match_items(pred_dec, gt_dec)
        
        pred_act = [a.model_dump() for a in record.action_items]
        gt_act = m["gt"].get("action_items", [])
        atp, afp, afn, ev_tp2, ev_fp2, ev_fn2, ow = match_items(pred_act, gt_act)
        
        total_dec_tp += dtp; total_dec_fp += dfp; total_dec_fn += dfn
        total_act_tp += atp; total_act_fp += afp; total_act_fn += afn
        total_ev_tp += (ev_tp1 + ev_tp2)
        total_ev_fp += (ev_fp1 + ev_fp2)
        total_ev_fn += (ev_fn1 + ev_fn2)
        total_owner += ow
        total_act_with_owner += len(gt_act)
        
    def safe_div(a, b): return a / b if b > 0 else 0.0
    
    dec_prec = safe_div(total_dec_tp, total_dec_tp + total_dec_fp) * 100
    dec_rec = safe_div(total_dec_tp, total_dec_tp + total_dec_fn) * 100
    
    act_prec = safe_div(total_act_tp, total_act_tp + total_act_fp) * 100
    act_rec = safe_div(total_act_tp, total_act_tp + total_act_fn) * 100
    
    ev_prec = safe_div(total_ev_tp, total_ev_tp + total_ev_fp) * 100
    ev_rec = safe_div(total_ev_tp, total_ev_tp + total_ev_fn) * 100
    
    owner_acc = safe_div(total_owner, total_act_with_owner) * 100
    
    f_out.write(f"- **Decision Precision:** {dec_prec:.1f}%\n")
    f_out.write(f"- **Decision Recall:** {dec_rec:.1f}%\n")
    f_out.write(f"- **Action Precision:** {act_prec:.1f}%\n")
    f_out.write(f"- **Action Recall:** {act_rec:.1f}%\n")
    f_out.write(f"- **Owner Accuracy:** {owner_acc:.1f}%\n")
    f_out.write(f"- **Evidence Precision:** {ev_prec:.1f}%\n")
    f_out.write(f"- **Evidence Recall:** {ev_rec:.1f}%\n")

def main():
    report_path = Path("baseline_report.md")
    with open(report_path, "w") as f:
        f.write("# Baseline Evaluation Report\n\n")
        f.write("## Pre-declared Thresholds (Gating for Phase 1/2)\n")
        for k, v in THRESHOLDS.items():
            f.write(f"- **{k}**: >= {v}%\n")
        
        print("Evaluating Track A: Clean...")
        evaluate_variant("clean", f)
        
        print("Evaluating Track A: Noisy...")
        evaluate_variant("noisy", f)
        
        f.write("\n## Track B: TTS Smoke Test\n")
        f.write("- **Status:** Not run (Deferred until real audio tracking is required)\n")
        
    print(f"\nBaseline report saved to {report_path.absolute()}")

if __name__ == "__main__":
    main()
