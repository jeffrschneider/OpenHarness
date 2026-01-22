#!/usr/bin/env python3
"""
Meeting Summary Formatter

Formats extracted meeting data into consistent Markdown or JSON output.

Usage:
    python formatter.py --format markdown < meeting_data.json
    python formatter.py --format json < meeting_data.json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any


def format_markdown(data: dict[str, Any]) -> str:
    """Format meeting data as Markdown."""
    lines = []

    # Meeting header
    meeting = data.get("meeting", {})
    if meeting.get("title"):
        lines.append(f"# {meeting['title']}")
    if meeting.get("date"):
        lines.append(f"*{meeting['date']}*")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append(data.get("summary", "No summary provided."))
    lines.append("")

    # Attendees
    attendees = meeting.get("attendees", [])
    if attendees:
        lines.append("## Attendees")
        for attendee in attendees:
            lines.append(f"- {attendee}")
        lines.append("")

    # Decisions
    decisions = data.get("decisions", [])
    if decisions:
        lines.append("## Decisions")
        for i, decision in enumerate(decisions, 1):
            if isinstance(decision, dict):
                lines.append(f"{i}. {decision.get('decision', '')}")
                if decision.get("context"):
                    lines.append(f"   - Context: {decision['context']}")
            else:
                lines.append(f"{i}. {decision}")
        lines.append("")

    # Action Items
    action_items = data.get("action_items", [])
    if action_items:
        lines.append("## Action Items")
        lines.append("| Owner | Action | Due | Priority |")
        lines.append("|-------|--------|-----|----------|")
        for item in action_items:
            owner = item.get("owner", "TBD")
            action = item.get("action", "")
            due = item.get("due_date") or "TBD"
            priority = item.get("priority", "medium")
            lines.append(f"| {owner} | {action} | {due} | {priority} |")
        lines.append("")

    # Parking Lot
    parking_lot = data.get("parking_lot", [])
    if parking_lot:
        lines.append("## Parking Lot")
        for item in parking_lot:
            lines.append(f"- {item}")
        lines.append("")

    # Next Meeting
    next_meeting = data.get("next_meeting", {})
    if next_meeting and (next_meeting.get("date") or next_meeting.get("time")):
        lines.append("## Next Meeting")
        parts = []
        if next_meeting.get("date"):
            parts.append(next_meeting["date"])
        if next_meeting.get("time"):
            parts.append(f"at {next_meeting['time']}")
        lines.append(" ".join(parts))
        agenda = next_meeting.get("agenda_items", [])
        if agenda:
            lines.append("")
            lines.append("**Agenda:**")
            for item in agenda:
                lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines)


def format_json(data: dict[str, Any]) -> str:
    """Format meeting data as pretty-printed JSON."""
    # Ensure consistent structure
    output = {
        "meeting": data.get("meeting", {}),
        "summary": data.get("summary", ""),
        "decisions": data.get("decisions", []),
        "action_items": data.get("action_items", []),
        "parking_lot": data.get("parking_lot", []),
        "next_meeting": data.get("next_meeting", {}),
        "formatted_at": datetime.utcnow().isoformat() + "Z",
    }
    return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Format meeting summary data into Markdown or JSON"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json", "md"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input JSON file (default: stdin)"
    )

    args = parser.parse_args()

    try:
        data = json.load(args.input_file)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format in ("markdown", "md"):
        output = format_markdown(data)
    else:
        output = format_json(data)

    print(output)


if __name__ == "__main__":
    main()
