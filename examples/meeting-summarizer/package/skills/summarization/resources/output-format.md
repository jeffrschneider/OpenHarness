# Output Format Specification

This document defines the structure for meeting summary output.

## JSON Schema

```json
{
  "meeting": {
    "title": "string",
    "date": "ISO8601 date",
    "attendees": ["string"]
  },
  "summary": "string (2-3 sentences)",
  "decisions": [
    {
      "decision": "string",
      "context": "string (optional)"
    }
  ],
  "action_items": [
    {
      "owner": "string",
      "action": "string",
      "due_date": "string or null",
      "priority": "high | medium | low"
    }
  ],
  "parking_lot": ["string"],
  "next_meeting": {
    "date": "string or null",
    "time": "string or null",
    "agenda_items": ["string"]
  }
}
```

## Markdown Template

```markdown
## Meeting Summary
<!-- 2-3 sentence overview -->

## Attendees
<!-- Bulleted list if known -->

## Decisions
<!-- Numbered list of decisions made -->

## Action Items
| Owner | Action | Due | Priority |
|-------|--------|-----|----------|
<!-- Table rows -->

## Parking Lot
<!-- Bulleted list of deferred items -->

## Next Meeting
<!-- Date, time, and any known agenda items -->
```

## Field Guidelines

### Summary
- Maximum 3 sentences
- Focus on outcomes, not process
- Answer: "What did this meeting accomplish?"

### Decisions
- Use past tense ("Decided to...", "Approved...", "Selected...")
- Include enough context to understand without reading full notes
- Order by importance or chronologically

### Action Items
- Start with verb (Send, Create, Review, Schedule...)
- Be specific enough to be actionable
- If no due date mentioned, mark as "TBD" not null
- Default priority to "medium" unless urgency signals present

### Parking Lot
- Keep items brief (one line each)
- Note why deferred if known ("blocked by X", "needs more research")
