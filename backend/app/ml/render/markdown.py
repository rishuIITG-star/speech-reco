from app.ml.schemas import MeetingRecord

def render_minutes(record: MeetingRecord) -> str:
    lines = []
    lines.append(f"# {record.summary}\n")
    
    if record.minutes:
        lines.append("## Minutes\n")
        for m in record.minutes:
            lines.append(f"### {m.title}")
            for p in m.points:
                lines.append(f"- {p}")
            lines.append("")
            
    if record.decisions:
        lines.append("## Decisions\n")
        for d in record.decisions:
            lines.append(f"- {d.text}")
        lines.append("")
        
    if record.proposals_not_agreed:
        lines.append("## Discussed but not agreed\n")
        for p in record.proposals_not_agreed:
            lines.append(f"- {p.text}")
        lines.append("")
        
    if record.action_items:
        lines.append("## Action Items\n")
        for a in record.action_items:
            lines.append(f"- [ ] {a.task} (Owner: {a.owner}, Deadline: {a.deadline})")
            
    return "\n".join(lines)
