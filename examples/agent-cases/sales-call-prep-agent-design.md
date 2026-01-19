# Sales Call Prep Agent - Design

## 1. Agent Identity

```yaml
name: Sales Call Prep Agent
slug: sales-call-prep-agent
version: 0.1.0
description: Researches prospects and prepares personalized briefings before sales calls
tags: [sales, research, business, productivity]
license: MIT
```

## 2. Architecture Overview

The Sales Call Prep Agent uses a **batch-parallel architecture** optimized for researching multiple prospects quickly. When given a list of companies, the agent dispatches research sub-agents in parallel—one per prospect—while a coordinator tracks progress and aggregates results.

The agent differentiates between **new prospects** (requiring full research) and **follow-ups** (requiring history retrieval plus delta research). For follow-ups, it retrieves previous conversation notes from memory and focuses research on "what's changed since last contact."

Prioritization is a core feature. The agent ranks prospects by opportunity value (deal size, signals of intent, timing) and presents briefings in priority order. This ensures the salesperson spends prep time where it matters most.

Memory is critical for this agent—it stores interaction history, objections raised, messaging that resonated, and pending action items. This transforms one-off research into cumulative relationship intelligence.

## 3. Sub-Agents

| Sub-Agent | Purpose | Inputs | Outputs | Runs In |
|-----------|---------|--------|---------|---------|
| company-researcher | Research a single company | company name, focus areas | company profile with news, signals | parallel (per company) |
| contact-researcher | Research individual contacts | person name, company, role | contact profile with background | parallel (per contact) |
| history-retriever | Pull previous interaction data | company name | past notes, objections, outcomes | parallel |
| priority-ranker | Score and rank prospects | list of researched prospects | prioritized list with reasoning | sequential (after research) |
| briefing-writer | Generate formatted briefing | prospect data, history, priorities | formatted briefing document | sequential (after ranking) |

```yaml
sub_agents:
  - name: company-researcher
    description: Deep research on a single company
    role: researcher
    tools: [WebSearch, WebFetch]
    delegated_tasks:
      - Find recent news (funding, acquisitions, leadership changes)
      - Identify company size, industry, tech stack
      - Detect pain point signals (job postings, reviews, complaints)
      - Find competitive positioning

  - name: contact-researcher
    description: Research individual contacts
    role: researcher
    tools: [WebSearch, WebFetch]
    delegated_tasks:
      - Find LinkedIn profile and career history
      - Identify recent posts or articles
      - Find mutual connections
      - Determine decision-making authority

  - name: history-retriever
    description: Retrieve past interaction data
    role: specialist
    tools: [Read]
    delegated_tasks:
      - Pull previous conversation notes
      - Identify objections raised
      - Find what messaging resonated
      - List pending action items

  - name: priority-ranker
    description: Score and prioritize prospects
    role: specialist
    tools: [Read]
    delegated_tasks:
      - Score by deal potential
      - Factor in timing signals
      - Consider relationship warmth
      - Rank for prep time allocation

  - name: briefing-writer
    description: Generate formatted briefings
    role: writer
    tools: [Read, Write]
    delegated_tasks:
      - Synthesize research into briefing format
      - Generate opening lines and talking points
      - Include relevant history context
      - Format for quick scanning
```

## 4. Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| sales-research | Best practices for prospect research | company-researcher, contact-researcher |
| pain-point-detection | Identifying buying signals | company-researcher |
| briefing-format | Standard briefing structure and style | briefing-writer |
| objection-handling | Common objections and responses | main agent (for history context) |

```
skills/
  sales-research/
    SKILL.md              # Research methodology and sources
    resources/
      signal-indicators.md
      research-checklist.md
    scripts/
      company-enricher.py
      linkedin-parser.py

  pain-point-detection/
    SKILL.md              # How to identify buying signals
    resources/
      signal-taxonomy.md
      job-posting-signals.md
      review-sentiment-signals.md

  briefing-format/
    SKILL.md              # Briefing structure guidelines
    resources/
      briefing-template.md
      quick-reference-template.md
    scripts/
      briefing-formatter.py

  objection-handling/
    SKILL.md              # Common objections by industry
    resources/
      objection-responses.md
      pricing-objections.md
```

## 5. Scripts

| Script | Purpose | Trigger | Language |
|--------|---------|---------|----------|
| company-enricher.py | Enrich company data from multiple sources | For each new prospect | Python |
| linkedin-parser.py | Extract structured data from LinkedIn | When researching contacts | Python |
| priority-scorer.py | Calculate priority scores | After all research complete | Python |
| briefing-formatter.py | Generate formatted briefing documents | At completion | Python |
| crm-sync.py | Sync notes back to CRM | After call (optional) | Python |

```yaml
scripts:
  - name: company-enricher.py
    path: skills/sales-research/scripts/company-enricher.py
    purpose: Aggregate company data from multiple sources
    inputs:
      - company_name: string
      - domain: string (optional)
    outputs:
      - profile:
          name: string
          industry: string
          size: string
          funding: string
          tech_stack: [string]
          recent_news: [news items]
    dependencies: [requests, beautifulsoup4]

  - name: linkedin-parser.py
    path: skills/sales-research/scripts/linkedin-parser.py
    purpose: Structure LinkedIn profile data
    inputs:
      - profile_url: string
      - or name + company: strings
    outputs:
      - contact:
          name: string
          title: string
          tenure: string
          previous_roles: [role objects]
          mutual_connections: [string]
          recent_activity: [post summaries]
    dependencies: [requests]

  - name: priority-scorer.py
    path: skills/sales-research/scripts/priority-scorer.py
    purpose: Calculate and rank prospect priorities
    inputs:
      - prospects: [prospect objects with signals]
      - weights: {deal_size, timing, warmth, signals}
    outputs:
      - ranked: [prospects with scores and reasoning]
    dependencies: []

  - name: briefing-formatter.py
    path: skills/briefing-format/scripts/briefing-formatter.py
    purpose: Generate formatted briefing document
    inputs:
      - prospects: [prospect objects]
      - format: [markdown | pdf | html]
      - include_cheatsheet: boolean
    outputs:
      - document: formatted content
      - cheatsheet: one-liner per prospect
    dependencies: [jinja2]

  - name: crm-sync.py
    path: skills/sales-research/scripts/crm-sync.py
    purpose: Sync research and notes back to CRM
    inputs:
      - prospect_id: string
      - notes: string
      - next_steps: [string]
    outputs:
      - success: boolean
      - crm_url: link to updated record
    dependencies: [requests]
```

## 6. MCP Integrations

| MCP Server | Purpose | Tools Exposed | Auth Type |
|------------|---------|---------------|-----------|
| salesforce | Pull deal history, update notes | contacts.read, opportunities.read, notes.write | oauth |
| hubspot | Alternative CRM integration | contacts.read, deals.read, notes.write | api-key |
| linkedin-sales-nav | Enhanced contact research | search, profile.read | oauth |
| calendar | Check call schedule | events.read | oauth |

```yaml
mcp_servers:
  - name: salesforce
    description: CRM integration for deal history and note storage
    protocol: http
    tools:
      - name: contacts.read
        enabled: true
        required: false
        description: Pull contact and account information
      - name: opportunities.read
        enabled: true
        required: false
        description: Get deal stage and history
      - name: notes.write
        enabled: true
        required: false
        description: Save research and call notes
    auth:
      type: oauth
      scopes: [api, refresh_token]

  - name: hubspot
    description: Alternative CRM integration
    protocol: http
    tools:
      - name: contacts.read
        enabled: true
        required: false
      - name: deals.read
        enabled: true
        required: false
      - name: notes.write
        enabled: true
        required: false
    auth:
      type: api-key
      env_var: HUBSPOT_API_KEY

  - name: linkedin-sales-nav
    description: Enhanced LinkedIn research for sales
    protocol: http
    tools:
      - name: search
        enabled: true
        required: false
        description: Search for contacts and companies
      - name: profile.read
        enabled: true
        required: false
        description: Get detailed profile information
    auth:
      type: oauth

  - name: calendar
    description: Access call schedule
    protocol: http
    tools:
      - name: events.read
        enabled: true
        required: false
        description: Get scheduled calls for prep prioritization
    auth:
      type: oauth
```

## 7. Memory Architecture

| Memory Type | Contents | Retention | Used For |
|-------------|----------|-----------|----------|
| product-context | Your product/service description, value props | persistent | Tailoring angles and talking points |
| prospect-history | Past interactions by company | archival | Recalling previous conversations |
| objection-log | Objections encountered and outcomes | archival | Learning what works |
| messaging-effectiveness | What messaging resonated with whom | archival | Refining approach over time |

```yaml
memory:
  - label: product-context
    purpose: Your offering for angle generation
    retention: persistent
    schema:
      product_name: string
      value_props: [string]
      ideal_customer: string
      differentiators: [string]
      pricing_model: string

  - label: prospect-history
    purpose: Interaction history by company
    retention: archival
    schema:
      company: string
      interactions:
        - date: date
          contact: string
          summary: string
          objections: [string]
          next_steps: [string]
          outcome: string

  - label: objection-log
    purpose: Track objections and responses
    retention: archival
    schema:
      entries:
        - objection: string
          context: string
          response_used: string
          outcome: [overcame | lost | pending]

  - label: messaging-effectiveness
    purpose: Learn what messaging works
    retention: archival
    schema:
      entries:
        - message_type: string
          industry: string
          persona: string
          effectiveness: [high | medium | low]
          notes: string
```

## 8. Tools Required

| Tool | Purpose | Permission Level |
|------|---------|------------------|
| WebSearch | Research companies and contacts | read |
| WebFetch | Get detailed information from sources | read |
| Read | Access skill resources and history | read |
| Write | Generate briefing documents | write |
| Task | Dispatch research sub-agents | execute |
| AskUserQuestion | Clarify scope and preferences | execute |

```yaml
tools:
  allowed:
    - WebSearch
    - WebFetch
    - Read
    - Write
    - Task
    - AskUserQuestion
  denied:
    - Bash
    - Edit
```

## 9. Workflow Diagram

```
User: "Prep me for 6 calls tomorrow"
    + [list of companies]
              │
              ▼
    ┌─────────────────────┐
    │     Main Agent      │
    │  (parse input, ask  │
    │   clarifying Qs)    │
    └─────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │  Categorize: New vs │
    │    Follow-up        │
    └─────────────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
[New Prospects]    [Follow-ups]
    │                   │
    ▼                   ▼
┌─────────┐       ┌─────────────┐
│ Parallel│       │History      │
│ Research│       │Retrieval +  │
│ (per co)│       │Delta Research│
└─────────┘       └─────────────┘
    │                   │
    │   ┌───────────────┘
    ▼   ▼
┌─────────────────────┐
│   Priority Ranker   │
│  (score & order)    │
└─────────────────────┘
              │
              ▼
┌─────────────────────┐
│  Briefing Writer    │
│ (generate per-      │
│  prospect briefings)│
└─────────────────────┘
              │
              ▼
┌─────────────────────┐
│  Present to User    │
│ (allow drill-down)  │
└─────────────────────┘
              │
         ┌────┴────┐
         ▼         ▼
   [More detail]  [Done]
         │         │
         └────┬────┘
              ▼
    ┌─────────────────────┐
    │  Save to Memory +   │
    │  Optional CRM Sync  │
    └─────────────────────┘
              │
              ▼
        Deliverables
```

## 10. Error Handling

| Failure Mode | Detection | Recovery |
|--------------|-----------|----------|
| Company not found | WebSearch returns no relevant results | Ask user for more details (domain, full name) |
| Contact not on LinkedIn | No profile found | Note as "limited info available", use other sources |
| CRM connection failed | Auth error or timeout | Proceed without CRM data; note for user |
| Research takes too long | Sub-agent exceeds timeout | Return partial results with "incomplete" flag |
| No signals found | Research returns generic info only | Be transparent: "No recent news or signals found" |
| History retrieval empty | No prior interactions in memory | Treat as new prospect |

## 11. Deliverable Specification

| Deliverable | Format | Generated By | Template |
|-------------|--------|--------------|----------|
| Prioritized briefings | Markdown | briefing-formatter.py | briefing-template.md |
| Quick-reference cheat sheet | Markdown table | briefing-formatter.py | quick-reference-template.md |
| Updated CRM notes | CRM entries | crm-sync.py | (API format) |
| Research summary | JSON (internal) | company-researcher | (structured data) |

---

## Design Checklist

- [x] Every capability in the Agent Case Description is addressed
- [x] Every interaction in the Example Session can be handled
- [x] Every Deliverable has a clear generation path
- [x] Sub-agents are used for parallelism where beneficial
- [x] Skills extract reusable knowledge from the system prompt
- [x] Scripts handle non-deterministic operations
- [x] MCPs are defined for external integrations
- [x] Memory captures what needs to persist
- [x] Error handling covers likely failure modes
- [x] The design is implementable on multiple harnesses (OAF-compliant)
