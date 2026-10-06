from app.ml.schemas import Transcript

def postfilter(transcript: Transcript) -> Transcript:
    filtered = []
    blocklist = ["thanks for watching", "subscribe to"]
    
    for seg in transcript.segments:
        if seg.no_speech_prob and seg.avg_logprob:
            if seg.no_speech_prob > 0.6 and seg.avg_logprob < -1.0:
                continue
                
        text_lower = seg.text.lower()
        if any(b in text_lower for b in blocklist):
            continue
            
        filtered.append(seg)
        
    for i, seg in enumerate(filtered):
        seg.id = i + 1
        
    transcript.segments = filtered
    return transcript
