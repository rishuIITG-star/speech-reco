import json
import argparse
from rapidfuzz import distance
from pathlib import Path

def calculate_wer(reference: str, hypothesis: str) -> float:
    ref_words = reference.lower().split()
    hyp_words = hypothesis.lower().split()
    if not ref_words:
        return 0.0 if not hyp_words else 100.0
    dist = distance.Levenshtein.distance(ref_words, hyp_words)
    return (dist / len(ref_words)) * 100

def evaluate_job(job_dir: Path):
    print(f"Evaluating job: {job_dir}")
    
    transcript_file = job_dir / "transcript.json"
    refined_file = job_dir / "refined.json"
    
    if not transcript_file.exists() or not refined_file.exists():
        print("Missing transcript or refined files. Cannot evaluate.")
        return
        
    with open(transcript_file) as f:
        transcript = json.load(f)
        
    with open(refined_file) as f:
        refined = json.load(f)
        
    # Dummy DER (Needs ground truth, so we mock or skip)
    print("DER: Requires labeled ground truth RTTM. Skipping.")
    
    # Calculate fallback percentage
    total_segments = len(refined.get("segments", []))
    if total_segments == 0:
        print("No segments found.")
        return
        
    changed = sum(1 for s in refined.get("segments", []) if s.get("changed"))
    fallback = total_segments - changed
    print(f"Segments changed: {changed} / {total_segments}")
    print(f"Fallback/Unchanged rate: {(fallback / total_segments) * 100:.1f}%")
    
    # Calculate WER between raw and refined (just as a metric of change)
    raw_text = " ".join([s.get("text", "") for s in transcript.get("segments", [])])
    ref_text = " ".join([s.get("text", "") for s in refined.get("segments", [])])
    wer_diff = calculate_wer(raw_text, ref_text)
    print(f"Refinement WER (difference from raw): {wer_diff:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", help="Job ID directory inside data/jobs/")
    args = parser.parse_args()
    
    if args.job:
        job_dir = Path("data/jobs") / args.job
        evaluate_job(job_dir)
    else:
        print("Please provide a --job ID.")
