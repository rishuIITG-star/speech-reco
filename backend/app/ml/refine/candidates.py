import jellyfish
from rapidfuzz import fuzz
from app.ml.schemas import Transcript

def get_candidates(transcript: Transcript, glossary: list) -> dict:
    if not glossary:
        return {}
        
    candidates = {}
    glossary_meta = {term: jellyfish.metaphone(term) for term in glossary}
    
    for seg in transcript.segments:
        for word in seg.words:
            w = word.w.strip(".,!?\"'")
            
            is_suspect = False
            if word.prob is not None and word.prob < 0.6:
                is_suspect = True
            elif word.prob is None and seg.avg_logprob is not None and seg.avg_logprob < -0.6:
                is_suspect = True
                
            if is_suspect:
                w_meta = jellyfish.metaphone(w)
                best_match = None
                best_score = 0
                for term, term_meta in glossary_meta.items():
                    if w_meta == term_meta:
                        score = 100
                    else:
                        score = fuzz.ratio(w.lower(), term.lower())
                        
                    if score > 80 and score > best_score:
                        best_score = score
                        best_match = term
                        
                if best_match:
                    candidates[w] = best_match
                    
    return candidates
