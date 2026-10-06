from app.ml.schemas import MeetingRecord
import csv
import io

def render_action_items_csv(record: MeetingRecord) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Task", "Owner", "Deadline", "Evidence"])
    
    for a in record.action_items:
        writer.writerow([a.task, a.owner, a.deadline, a.evidence])
    if record.proposals_not_agreed:
        writer.writerow([])
        writer.writerow(["Discussed but not agreed (Proposals)"])
        writer.writerow(["Proposal", "Evidence"])
        for p in record.proposals_not_agreed:
            writer.writerow([p.text, p.evidence])
            
    return output.getvalue()
