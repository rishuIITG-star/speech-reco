import pytest
from app.core.errors import AppError, map_error_to_status
from app.ml.refine.guards import validate_segment

def test_error_mapping():
    assert map_error_to_status("NO_SPEECH") == 422
    assert map_error_to_status("INVALID_AUDIO") == 422
    assert map_error_to_status("LLM_FAILED") == 500
    assert map_error_to_status("SCHEMA_INVALID") == 500

def test_validate_segment_succeeds():
    orig = "This is a valid sentence with one number 1."
    ref = "This is a valid sentence with one number 1."
    is_valid, reason = validate_segment(orig, ref)
    assert is_valid
    
def test_validate_segment_numbers_fail():
    orig = "We agreed on 5 points."
    ref = "We agreed on 6 points."
    is_valid, reason = validate_segment(orig, ref)
    assert not is_valid
    assert "Numbers" in reason

def test_validate_segment_negations_fail():
    orig = "I will not do that."
    ref = "I will do that."
    is_valid, reason = validate_segment(orig, ref)
    assert not is_valid
    assert "Negations" in reason

def test_validate_segment_length_insane():
    orig = "Yes."
    ref = "Yes, I completely agree with everything you just said and more."
    is_valid, reason = validate_segment(orig, ref)
    assert not is_valid
    assert "Length ratio" in reason
