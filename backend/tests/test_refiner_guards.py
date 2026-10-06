import pytest
from app.ml.refine.guards import validate_segment

def test_refiner_guards():
    original = "we will not ship fifteen units of cooper netties"
    
    # 1. Valid fix
    valid_fix = "we will not ship fifteen units of Kubernetes"
    is_valid, reason = validate_segment(original, valid_fix)
    assert is_valid, f"Should keep valid term fix: {reason}"
    
    # 2. Drops not
    drops_not = "we will ship fifteen units of Kubernetes"
    is_valid, reason = validate_segment(original, drops_not)
    assert not is_valid
    assert "Negations" in reason
    
    # 3. Changes number
    changes_num = "we will not ship fifty units of Kubernetes"
    is_valid, reason = validate_segment(original, changes_num)
    assert not is_valid
    assert "Numbers" in reason
    
    # 4. Changes modal
    changes_modal = "we should not ship fifteen units of Kubernetes"
    is_valid, reason = validate_segment(original, changes_modal)
    assert not is_valid
    assert "Modals" in reason
    
    # 5. Over-editing (Change ratio > 15%)
    over_edited = "we will not ship fifteen units of Kubernetes because it's bad"
    is_valid, reason = validate_segment(original, over_edited)
    assert not is_valid
    assert "Change ratio" in reason
