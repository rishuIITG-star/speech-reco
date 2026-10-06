from typing import List
from app.ml.schemas import RefinedTranscript

def chunk_transcript(transcript: RefinedTranscript, window_duration: float = 300, overlap: float = 30) -> List[List[dict]]:
    # Very basic chunker based on number of segments (approximating 5 mins)
    # A real implementation would use segment timestamps
    chunks = []
    chunk = []
    for i, seg in enumerate(transcript.segments):
        chunk.append({"id": seg.id, "text": seg.text})
        if len(chunk) >= 50: # Roughly 5 mins if 6s per segment
            chunks.append(chunk)
            # overlap
            chunk = chunk[-10:] if len(chunk) > 10 else []
            
    if chunk and (not chunks or chunk != chunks[-1]):
        chunks.append(chunk)
        
    if not chunks:
        chunks = [[]]
        
    return chunks
