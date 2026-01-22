---
# OAF Identity (required)
name: Meeting Summarizer Agent
vendorKey: openharness
agentKey: meeting-summarizer
version: 0.1.0
slug: meeting-summarizer-agent

# Metadata (required)
description: Transforms meeting notes or transcripts into structured summaries with action items
author: OpenHarness Contributors
license: MIT
tags: [productivity, meetings, summarization, skills-pattern]

# Model Configuration
model: sonnet

# Orchestration
entrypoint: structured
---

# Meeting Summarizer Agent

This agent demonstrates the **skills pattern** with a `scripts/` directory. It transforms raw meeting notes or transcripts into structured, actionable summaries.

## Composition Pattern

This sample showcases:
- **Skills** with resources and scripts
- **Scripts** for structured output formatting (`scripts/formatter.py`)

## Purpose

Take unstructured meeting content and produce:
1. A concise summary (2-3 sentences)
2. Key decisions made
3. Action items with owners and due dates
4. Open questions or parking lot items
5. Next meeting date (if mentioned)

## Skills

This agent uses the following skill:

| Skill | Purpose |
|-------|---------|
| summarization | Guidelines for extracting key information and formatting output |

The summarization skill includes a `scripts/formatter.py` that structures the output into consistent JSON or Markdown formats.

## How It Works

1. User provides meeting notes, transcript, or recording summary
2. Agent extracts key information following summarization guidelines
3. Agent uses `formatter.py` script to structure the output
4. Returns formatted summary in user's preferred format (JSON or Markdown)

## Example Input

```
Team sync 1/15 - John, Sarah, Mike attending

Discussed Q1 roadmap. Sarah presented the new design mockups, everyone liked
the simplified nav. Mike raised concerns about timeline - we're already behind
on the API work. John said he can pull in a contractor to help.

Decided to push the beta launch to Feb 15 instead of Feb 1. Sarah will finalize
designs by Friday. Mike to send contractor requirements to John by EOD tomorrow.

Need to figure out the pricing model still - table for next week.

Next sync: Tuesday 1/21 at 2pm
```

## Example Output (Markdown)

```markdown
## Meeting Summary
Team sync discussing Q1 roadmap. Agreed to delay beta launch by two weeks
due to API timeline concerns. Contractor support approved to accelerate work.

## Decisions
- Beta launch pushed from Feb 1 to Feb 15
- Will bring in contractor for API work

## Action Items
| Owner | Action | Due |
|-------|--------|-----|
| Sarah | Finalize design mockups | Friday 1/17 |
| Mike | Send contractor requirements to John | EOD 1/16 |
| John | Review contractor requirements | After Mike sends |

## Parking Lot
- Pricing model (deferred to next meeting)

## Next Meeting
Tuesday, January 21 at 2:00 PM
```

## Tools

**Allowed:** Read (for processing uploaded transcripts)
**Denied:** WebSearch, Bash, Edit
