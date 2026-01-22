---
name: summarization
description: Guidelines for extracting key meeting information and formatting structured output. Includes formatter script for consistent JSON/Markdown output.
---

# Summarization Skill

This skill provides methodology for summarizing meetings and a script for formatting output consistently.

## Overview

The summarization skill helps the agent:
1. Identify what's important in meeting content
2. Categorize information correctly (decision vs. action item vs. discussion)
3. Format output consistently using the formatter script

## Extraction Guidelines

### What Counts as a Decision?
- Explicit agreement ("we decided...", "agreed to...", "will go with...")
- Resolved debates or choices between options
- Approved plans, budgets, or timelines

### What Counts as an Action Item?
Must have:
- A clear task (what needs to be done)
- An owner (who will do it)
- Ideally a due date (when it's due)

Look for: "will", "going to", "needs to", "should", "by [date]", names followed by tasks

### What Goes in Parking Lot?
- Topics raised but explicitly deferred
- Questions no one could answer
- Items marked for "later", "next time", "offline"

### What's Just Context?
- Background information
- Status updates without decisions
- General discussion that didn't lead anywhere

## Output Formats

The `scripts/formatter.py` script supports two output formats:
- **Markdown** (default): Human-readable, good for sharing
- **JSON**: Machine-readable, good for integrations

## Resources

- `resources/output-format.md` - Detailed output format specification

## Scripts

- `scripts/formatter.py` - Formats extracted meeting data into consistent structure
