import pytest
from app.ml.schemas import ActionItem, Decision, ProposalNotAgreed
from app.ml.extract.grounding import is_hedging, check_owner_deadline, ground_items

def test_is_hedging():
    assert is_hedging("should we do this?") is True
    assert is_hedging("let's go with this") is False
    assert is_hedging("maybe we can do this") is True

def test_check_owner_deadline():
    item = ActionItem(task="test", owner="Marcus", deadline="Friday", timestamp=0.0, evidence="Marcus will do it by Friday", segment_ids=[1])
    # match case insensitive
    window_text = "Yes, Marcus will do it by Friday."
    downgraded = check_owner_deadline(item, window_text)
    assert not downgraded
    assert item.owner == "Marcus"
    
    # mismatch
    window_text_2 = "Yes, Elena will do it by next week."
    downgraded = check_owner_deadline(item, window_text_2)
    assert downgraded
    assert item.owner == "unspecified"
    assert item.deadline == "unspecified"

def test_ground_items():
    items = {
        "decisions": [
            Decision(text="Migrate to K8s", timestamp=0.0, evidence="we have consensus to execute", segment_ids=[1]),
            Decision(text="Fake decision", timestamp=0.0, evidence="should we migrate?", segment_ids=[2]),
        ],
        "action_items": []
    }
    
    from app.ml.schemas import Segment
    segments = [
        Segment(id=1, start=0.0, end=1.0, text="Priya confirmed we have consensus to execute."),
        Segment(id=2, start=1.0, end=2.0, text="Should we migrate?")
    ]
    
    grounded, report = ground_items(items, segments)
    assert len(grounded["decisions"]) == 1
    assert len(grounded["proposals_not_agreed"]) == 1
    
    assert grounded["decisions"][0].text == "Migrate to K8s"
    assert grounded["proposals_not_agreed"][0].text == "Fake decision"
