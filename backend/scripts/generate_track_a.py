import json
from pathlib import Path
import os

TRACK_A_DIR = Path("backend/benchmark_data/track_a")

MEETINGS = [
    {
        "id": "meeting_1",
        "clean": [
            {"id": 1, "start": 0.0, "end": 5.0, "speaker_id": "SPEAKER_00", "text": "Alright, let's kick off the project. I've decided we will migrate to PostgreSQL."},
            {"id": 2, "start": 5.0, "end": 8.5, "speaker_id": "SPEAKER_01", "text": "Sounds good. Alice, can you review the database schema by next Friday?"},
            {"id": 3, "start": 8.5, "end": 10.0, "speaker_id": "SPEAKER_02", "text": "Yes, I will have it done."}
        ],
        "noisy": [
            {"id": 1, "start": 0.0, "end": 5.0, "speaker_id": "SPEAKER_00", "text": "all right lets kickoff the project decided we migrate to post grass"},
            {"id": 2, "start": 5.0, "end": 8.5, "speaker_id": "SPEAKER_01", "text": "sounds good alice review database schema next fry day"},
            {"id": 3, "start": 8.5, "end": 10.0, "speaker_id": "SPEAKER_02", "text": "yes I will haven done"}
        ],
        "gt": {
            "decisions": [{"text": "Migrate to PostgreSQL", "evidence_segment_ids": [1]}],
            "action_items": [{"text": "Review database schema", "owner": "Alice", "deadline": "next Friday", "evidence_segment_ids": [2, 3]}]
        }
    },
    {
        "id": "meeting_2",
        "clean": [
            {"id": 1, "start": 0.0, "end": 4.0, "speaker_id": "SPEAKER_00", "text": "Welcome to the budget review. We need to cut the Q3 marketing spend by 15%."},
            {"id": 2, "start": 4.0, "end": 7.0, "speaker_id": "SPEAKER_01", "text": "That's a steep cut, but I agree we have to do it."},
            {"id": 3, "start": 7.0, "end": 12.0, "speaker_id": "SPEAKER_00", "text": "Great. Bob, please send the revised Q3 budget to the board by tomorrow morning."}
        ],
        "noisy": [
            {"id": 1, "start": 0.0, "end": 4.0, "speaker_id": "SPEAKER_00", "text": "welcome to budget review need to cut cue three marketing spend fifteen percent"},
            {"id": 2, "start": 4.0, "end": 7.0, "speaker_id": "SPEAKER_01", "text": "steep cut agree have to do"},
            {"id": 3, "start": 7.0, "end": 12.0, "speaker_id": "SPEAKER_00", "text": "great bob send revise cue three budget board tomorrow morning"}
        ],
        "gt": {
            "decisions": [{"text": "Cut Q3 marketing spend by 15%", "evidence_segment_ids": [1, 2]}],
            "action_items": [{"text": "Send revised Q3 budget to the board", "owner": "Bob", "deadline": "tomorrow morning", "evidence_segment_ids": [3]}]
        }
    },
    {
        "id": "meeting_3",
        "clean": [
            {"id": 1, "start": 0.0, "end": 6.0, "speaker_id": "SPEAKER_01", "text": "The new logo looks good, but the color is off. Let's change the primary color to hex 1A2B3C."},
            {"id": 2, "start": 6.0, "end": 9.0, "speaker_id": "SPEAKER_02", "text": "I can make that change right now. Should I also update the typography?"},
            {"id": 3, "start": 9.0, "end": 12.0, "speaker_id": "SPEAKER_01", "text": "No, keep the font as is for now. Just update the color by EOD."}
        ],
        "noisy": [
            {"id": 1, "start": 0.0, "end": 6.0, "speaker_id": "SPEAKER_01", "text": "new logo looks good color is off lets change primary color to text one a two b three c"},
            {"id": 2, "start": 6.0, "end": 9.0, "speaker_id": "SPEAKER_02", "text": "make change right now update typo graphy"},
            {"id": 3, "start": 9.0, "end": 12.0, "speaker_id": "SPEAKER_01", "text": "no keep font as is update color end of day"}
        ],
        "gt": {
            "decisions": [{"text": "Change primary logo color to #1A2B3C", "evidence_segment_ids": [1]}, {"text": "Keep current typography/font", "evidence_segment_ids": [3]}],
            "action_items": [{"text": "Update logo color", "owner": "SPEAKER_02", "deadline": "EOD", "evidence_segment_ids": [2, 3]}]
        }
    },
    {
        "id": "meeting_4",
        "clean": [
            {"id": 1, "start": 0.0, "end": 5.0, "speaker_id": "SPEAKER_00", "text": "We are switching our cloud provider from AWS to GCP starting next month."},
            {"id": 2, "start": 5.0, "end": 8.0, "speaker_id": "SPEAKER_01", "text": "Charlie, you'll lead the infrastructure migration team."},
            {"id": 3, "start": 8.0, "end": 11.0, "speaker_id": "SPEAKER_02", "text": "Got it. I will draft the migration plan by October 15th."}
        ],
        "noisy": [
            {"id": 1, "start": 0.0, "end": 5.0, "speaker_id": "SPEAKER_00", "text": "switching cloud provider from a w as to g c p start next month"},
            {"id": 2, "start": 5.0, "end": 8.0, "speaker_id": "SPEAKER_01", "text": "charlie youll lead infra structure team"},
            {"id": 3, "start": 8.0, "end": 11.0, "speaker_id": "SPEAKER_02", "text": "got it draft migration plan october fifteen"}
        ],
        "gt": {
            "decisions": [{"text": "Switch cloud provider from AWS to GCP", "evidence_segment_ids": [1]}],
            "action_items": [{"text": "Draft infrastructure migration plan", "owner": "Charlie", "deadline": "October 15th", "evidence_segment_ids": [2, 3]}]
        }
    },
    {
        "id": "meeting_5",
        "clean": [
            {"id": 1, "start": 0.0, "end": 4.0, "speaker_id": "SPEAKER_01", "text": "The Q4 roadmap is finalized. We'll drop the mobile app feature for now."},
            {"id": 2, "start": 4.0, "end": 8.0, "speaker_id": "SPEAKER_00", "text": "Wait, we can't drop it. Let's just delay it to Q1 instead of dropping entirely."},
            {"id": 3, "start": 8.0, "end": 10.0, "speaker_id": "SPEAKER_01", "text": "Okay, agreed. Delay to Q1."},
            {"id": 4, "start": 10.0, "end": 14.0, "speaker_id": "SPEAKER_02", "text": "Diana, please update the JIRA board to reflect the Q1 shift by tonight."}
        ],
        "noisy": [
            {"id": 1, "start": 0.0, "end": 4.0, "speaker_id": "SPEAKER_01", "text": "q four road map finalize drop mobile app feature"},
            {"id": 2, "start": 4.0, "end": 8.0, "speaker_id": "SPEAKER_00", "text": "cant drop it delay to queue one instead"},
            {"id": 3, "start": 8.0, "end": 10.0, "speaker_id": "SPEAKER_01", "text": "ok agree delay queue one"},
            {"id": 4, "start": 10.0, "end": 14.0, "speaker_id": "SPEAKER_02", "text": "diana update jira board shift tonight"}
        ],
        "gt": {
            "decisions": [{"text": "Delay mobile app feature to Q1 (instead of dropping)", "evidence_segment_ids": [2, 3]}],
            "action_items": [{"text": "Update JIRA board with Q1 shift", "owner": "Diana", "deadline": "tonight", "evidence_segment_ids": [4]}]
        }
    }
]

def main():
    clean_dir = TRACK_A_DIR / "clean"
    noisy_dir = TRACK_A_DIR / "noisy"
    clean_dir.mkdir(parents=True, exist_ok=True)
    noisy_dir.mkdir(parents=True, exist_ok=True)

    for m in MEETINGS:
        # Clean
        with open(clean_dir / f"{m['id']}_transcript.json", "w") as f:
            json.dump(m["clean"], f, indent=2)
        with open(clean_dir / f"{m['id']}_gt.json", "w") as f:
            json.dump(m["gt"], f, indent=2)
            
        # Noisy
        with open(noisy_dir / f"{m['id']}_transcript.json", "w") as f:
            json.dump(m["noisy"], f, indent=2)
        with open(noisy_dir / f"{m['id']}_gt.json", "w") as f:
            json.dump(m["gt"], f, indent=2)
            
    print(f"Generated {len(MEETINGS)} Track A meetings in clean and noisy variants.")

if __name__ == "__main__":
    main()
