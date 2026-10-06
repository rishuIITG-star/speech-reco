import pytest
from app.ml.schemas import ActionItem, Decision, ProposalNotAgreed, RefinedSegment, UNSPEC
from app.ml.extract.grounding import ground_items

def test_grounding_enforces_rules():
    segments = [
        RefinedSegment(id=1, text="Maybe we should upgrade the database.", start=0.0, end=2.0),
        RefinedSegment(id=2, text="Alice will migrate the data by next week.", start=2.0, end=4.0),
        RefinedSegment(id=3, text="Let's go with Postgres.", start=4.0, end=5.0)
    ]
    
    items = {
        "decisions": [
            # Fabricated evidence (should drop)
            Decision(text="Use Mongo", evidence="We agreed on Mongo", segment_ids=[3]),
            # Proposal masquerading as decision (should downgrade)
            Decision(text="Upgrade DB", evidence="Maybe we should upgrade the database", segment_ids=[1]),
            # Valid decision
            Decision(text="Use Postgres", evidence="Let's go with Postgres.", segment_ids=[3])
        ],
        "action_items": [
            # Valid owner and deadline
            ActionItem(task="Migrate data", owner="Alice", deadline="next week", evidence="Alice will migrate the data by next week.", segment_ids=[2]),
            # Owner not in text
            ActionItem(task="Setup server", owner="Bob", deadline="tomorrow", evidence="Alice will migrate the data by next week.", segment_ids=[2]),
            # Speaker as owner
            ActionItem(task="Check logs", owner="SPEAKER_01", deadline="next week", evidence="Alice will migrate the data by next week.", segment_ids=[2])
        ],
        "proposals_not_agreed": []
    }
    
    grounded, report = ground_items(items, segments)
    
    # Check decisions
    assert len(grounded["decisions"]) == 1
    assert grounded["decisions"][0].text == "Use Postgres"
    
    # Check proposals (1 downgraded from decision)
    assert len(grounded["proposals_not_agreed"]) == 1
    assert grounded["proposals_not_agreed"][0].text == "Upgrade DB"
    
    # Check actions
    actions = grounded["action_items"]
    assert len(actions) == 3
    
    # Valid
    assert actions[0].owner == "Alice"
    assert actions[0].deadline == "next week"
    
    # Fabricated owner/deadline
    assert actions[1].owner == UNSPEC
    assert actions[1].deadline == UNSPEC
    
    # Speaker as owner
    assert actions[2].owner == UNSPEC
