from collections import Counter
from app.ml.schemas import Edit, Segment

import re
from difflib import SequenceMatcher

NEGATIONS = {"not", "no", "never", "none", "nobody", "nothing", "neither", "nor", "cannot", "without"}
MODALS = {"will", "would", "shall", "should", "can", "could", "may", "might", "must"}
SPELLED_NUMBERS = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million", "billion"}

def extract_numbers(text: str) -> Counter:
    words = text.lower().replace('-', ' ').split()
    nums = []
    for w in words:
        clean = "".join(c for c in w if c.isalnum())
        if any(char.isdigit() for char in clean):
            nums.append(clean)
        elif clean in SPELLED_NUMBERS:
            nums.append(clean)
    return Counter(nums)

def extract_set(text: str, target_set: set, is_negation=False) -> Counter:
    words = text.lower().split()
    found = []
    # Check for "going to"
    if not is_negation and "going to" in text.lower():
        found.extend(["going to"] * text.lower().count("going to"))
        
    for w in words:
        clean_w = "".join(c for c in w if c.isalpha() or c == "'")
        if clean_w in target_set:
            found.append(clean_w)
        elif is_negation and clean_w.endswith("n't"):
            found.append("not") # Normalize n't to not
    return Counter(found)

def validate_segment(original: str, refined: str, glossary: list = None) -> tuple[bool, str]:
    if extract_numbers(original) != extract_numbers(refined):
        return False, "Numbers changed"
        
    if extract_set(original, NEGATIONS, is_negation=True) != extract_set(refined, NEGATIONS, is_negation=True):
        return False, "Negations changed"
        
    if extract_set(original, MODALS) != extract_set(refined, MODALS):
        return False, "Modals/Commitments changed"
        
    if glossary:
        for term in glossary:
            term_lower = term.lower()
            if term_lower in original.lower() and term_lower not in refined.lower():
                return False, f"Removed glossary term: {term}"
        
    # Word-level change ratio (max 15% change)
    orig_words = original.split()
    ref_words = refined.split()
    
    if len(orig_words) > 0:
        sm = SequenceMatcher(None, orig_words, ref_words)
        # Ratio is 2*M / (T), distance is 1 - ratio
        change_ratio = 1.0 - sm.ratio()
        if change_ratio > 0.25:
            return False, "Change ratio exceeds 25%"
            
    return True, "ok"
