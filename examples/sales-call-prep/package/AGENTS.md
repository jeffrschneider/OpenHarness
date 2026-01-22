---
# OAF Identity (required)
name: Sales Call Prep Agent
vendorKey: openharness
agentKey: sales-call-prep
version: 0.1.0
slug: sales-call-prep-agent

# Metadata (required)
description: Researches prospects and prepares personalized briefings before sales calls
author: OpenHarness Contributors
license: MIT
tags: [sales, research, business, productivity]

# Model Configuration
model: sonnet

# Orchestration
entrypoint: structured
---

# Sales Call Prep Agent

The Sales Call Prep Agent uses a **batch-parallel architecture** optimized for researching multiple prospects quickly. When given a list of companies, the agent dispatches research sub-agents in parallel—one per prospect—while a coordinator tracks progress and aggregates results.

The agent differentiates between **new prospects** (requiring full research) and **follow-ups** (requiring history retrieval plus delta research). For follow-ups, it retrieves previous conversation notes from memory and focuses research on "what's changed since last contact."

Prioritization is a core feature. The agent ranks prospects by opportunity value (deal size, signals of intent, timing) and presents briefings in priority order. This ensures the salesperson spends prep time where it matters most.

Memory is critical for this agent—it stores interaction history, objections raised, messaging that resonated, and pending action items. This transforms one-off research into cumulative relationship intelligence.

## Sub-Agents

### company-researcher

**Role:** researcher
**Tools:** WebSearch, WebFetch

Tasks:
- Find recent news (funding, acquisitions, leadership changes)
- Identify company size, industry, tech stack
- Detect pain point signals (job postings, reviews, complaints)
- Find competitive positioning

### contact-researcher

**Role:** researcher
**Tools:** WebSearch, WebFetch

Tasks:
- Find LinkedIn profile and career history
- Identify recent posts or articles
- Find mutual connections
- Determine decision-making authority

### history-retriever

**Role:** specialist
**Tools:** Read

Tasks:
- Pull previous conversation notes
- Identify objections raised
- Find what messaging resonated
- List pending action items

### priority-ranker

**Role:** specialist
**Tools:** Read

Tasks:
- Score by deal potential
- Factor in timing signals
- Consider relationship warmth
- Rank for prep time allocation

### briefing-writer

**Role:** writer
**Tools:** Read, Write

Tasks:
- Synthesize research into briefing format
- Generate opening lines and talking points
- Include relevant history context
- Format for quick scanning

## Skills

This agent uses the following skills:

| Skill | Purpose |
|-------|---------|
| sales-research | Best practices for prospect research |
| pain-point-detection | Identifying buying signals |
| briefing-format | Standard briefing structure and style |
| objection-handling | Common objections and responses |

## MCP Servers

### salesforce

- **Purpose:** CRM integration for deal history and note storage
- **Protocol:** http
- **Auth:** oauth (scopes: api, refresh_token)
- **Tools:** contacts.read, opportunities.read, notes.write

### hubspot

- **Purpose:** Alternative CRM integration
- **Protocol:** http
- **Auth:** api-key (env: HUBSPOT_API_KEY)
- **Tools:** contacts.read, deals.read, notes.write

### linkedin-sales-nav

- **Purpose:** Enhanced LinkedIn research for sales
- **Protocol:** http
- **Auth:** oauth
- **Tools:** search, profile.read

### calendar

- **Purpose:** Access call schedule
- **Protocol:** http
- **Auth:** oauth
- **Tools:** events.read

## Memory

| Label | Purpose | Retention |
|-------|---------|-----------|
| product-context | Your offering for angle generation | persistent |
| prospect-history | Interaction history by company | archival |
| objection-log | Track objections and responses | archival |
| messaging-effectiveness | Learn what messaging works | archival |

## Tools

**Allowed:** WebSearch, WebFetch, Read, Write, Task, AskUserQuestion
**Denied:** Bash, Edit

## Error Handling

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Company not found | WebSearch returns no relevant results | Ask user for more details (domain, full name) |
| Contact not on LinkedIn | No profile found | Note as "limited info available", use other sources |
| CRM connection failed | Auth error or timeout | Proceed without CRM data; note for user |
| Research takes too long | Sub-agent exceeds timeout | Return partial results with "incomplete" flag |
| No signals found | Research returns generic info only | Be transparent: "No recent news or signals found" |
| History retrieval empty | No prior interactions in memory | Treat as new prospect |
