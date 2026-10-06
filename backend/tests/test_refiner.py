import pytest
from app.ml.schemas import Edit, Segment
from app.ml.refine.guards import apply_edit

def test_apply_edit_valid():
    seg = Segment(id=1, start=0.0, end=1.0, text="We should use cooper netties")
    edit = Edit(segment_id=1, original="cooper netties", corrected="Kubernetes", reason="glossary", status="applied")
    res = apply_edit(edit, seg)
    assert res.status == "applied"

def test_apply_edit_changes_numbers():
    seg = Segment(id=1, start=0.0, end=1.0, text="We have 15 units")
    edit = Edit(segment_id=1, original="15 units", corrected="50 units", reason="", status="applied")
    res = apply_edit(edit, seg)
    assert res.status == "rejected"
    assert "Number" in res.reject_reason

def test_apply_edit_changes_negations():
    seg = Segment(id=1, start=0.0, end=1.0, text="We will not ship")
    edit = Edit(segment_id=1, original="will not ship", corrected="will ship", reason="", status="applied")
    res = apply_edit(edit, seg)
    assert res.status == "rejected"
    assert "Negations" in res.reject_reason

def test_apply_edit_changes_modals():
    seg = Segment(id=1, start=0.0, end=1.0, text="We will build it")
    edit = Edit(segment_id=1, original="will build", corrected="should build", reason="", status="applied")
    res = apply_edit(edit, seg)
    assert res.status == "rejected"
    assert "Modal" in res.reject_reason
