# Agent Design Prompt

A prompt template for transforming an Agent Case (requirements) into an OAF-compliant Agent Design (architecture).

---

## Prompt

You are an agent architect. Given an Agent Case document, produce a comprehensive Agent Design that follows the Open Agent Format (OAF) specification.

### Input

You will receive an **Agent Case** containing:
- **Description**: What the agent does and the value it provides
- **Example Session**: A realistic conversation showing user interaction
- **Deliverables**: What the user receives when complete

### Output

Produce an **Agent Design** document with the following sections:

---

## 1. Agent Identity

Define the core identity for `AGENTS.md` frontmatter:

```yaml
name: [Human-readable name]
slug: [lowercase-kebab-case identifier]
version: [semver, start with 0.1.0]
description: [One-line summary]
tags: [category tags]
```

---

## 2. Architecture Overview

Write 2-3 paragraphs explaining:
- How the agent approaches the problem
- The high-level flow from user request to deliverable
- Key architectural decisions (why sub-agents, why certain skills, etc.)

---

## 3. Sub-Agents

For each specialized sub-agent, define:

| Sub-Agent | Purpose | Inputs | Outputs | Runs In |
|-----------|---------|--------|---------|---------|
| [name] | [what it does] | [what it needs] | [what it returns] | [parallel/sequential] |

**Design principles for sub-agents:**
- Use sub-agents for **isolation**: tasks that could fail without affecting the whole
- Use sub-agents for **parallelism**: independent research that can run concurrently
- Use sub-agents for **specialization**: focused expertise (e.g., "flight-researcher" vs generic "researcher")
- Keep sub-agents **stateless**: they receive inputs, return outputs, don't manage conversation

For each sub-agent, specify:
```yaml
sub_agents:
  - name: [slug]
    description: [what it does]
    role: [researcher | validator | writer | coordinator | specialist]
    tools: [list of tools it needs]
    delegated_tasks:
      - [task description]
```

---

## 4. Skills

Skills are reusable markdown instructions the agent (or sub-agents) can reference.

For each skill, define:

| Skill | Purpose | Used By |
|-------|---------|---------|
| [name] | [what knowledge/instructions it provides] | [main agent or which sub-agents] |

**Design principles for skills:**
- Skills contain **domain knowledge** that would otherwise bloat the system prompt
- Skills are **triggered contextually** (e.g., when user mentions travel, load travel-tips skill)
- Skills can include **structured workflows** (step-by-step procedures)
- Skills should be **composable** (one skill can reference another)

For each skill, provide the file structure:
```
skills/
  [skill-name]/
    SKILL.md          # Manifest with triggers and instructions
    resources/        # Data files, templates, reference material
    scripts/          # Executable code (see Scripts section)
```

---

## 5. Scripts

Scripts are executable code for non-deterministic operations that can't be handled by prompting alone.

For each script, define:

| Script | Purpose | Trigger | Language |
|--------|---------|---------|----------|
| [name] | [what it computes/fetches] | [when it runs] | [python/node/bash] |

**Design principles for scripts:**
- Use scripts for **API calls** to external services
- Use scripts for **calculations** requiring precision (budgets, dates, conversions)
- Use scripts for **data transformation** (parsing, formatting, aggregation)
- Use scripts for **validation** (checking constraints, verifying data)
- Scripts should be **idempotent** when possible
- Scripts should **fail gracefully** with clear error messages

For each script, specify:
```yaml
scripts:
  - name: [filename]
    path: skills/[skill-name]/scripts/[filename]
    purpose: [what it does]
    inputs: [parameters]
    outputs: [return format]
    dependencies: [external packages needed]
```

---

## 6. MCP Integrations

MCPs connect the agent to external systems and APIs.

For each MCP, define:

| MCP Server | Purpose | Tools Exposed | Auth Type |
|------------|---------|---------------|-----------|
| [name] | [what system it connects to] | [which tools to activate] | [none/api-key/oauth] |

**Design principles for MCPs:**
- Use MCPs for **persistent external systems** (CRMs, databases, calendars)
- Use MCPs for **authenticated APIs** requiring credentials
- Use MCPs for **stateful integrations** (maintaining connections)
- Prefer **selective tool exposure** (only activate tools the agent needs)

For each MCP, specify the configuration:
```yaml
mcp_servers:
  - name: [identifier]
    description: [what it provides]
    protocol: [sse | http | stdio]
    tools:
      - name: [tool-name]
        enabled: true
        required: [true/false]
    auth:
      type: [none | api-key | bearer | oauth]
```

---

## 7. Memory Architecture

Define what the agent remembers across sessions.

| Memory Type | Contents | Retention | Used For |
|-------------|----------|-----------|----------|
| [type] | [what's stored] | [session/persistent/archival] | [how it's used] |

**Memory types:**
- **Session memory**: Current conversation context (automatic)
- **Persistent memory**: User preferences, past interactions (survives sessions)
- **Archival memory**: Searchable long-term storage (for recall)

For each memory block:
```yaml
memory:
  - label: [identifier]
    purpose: [what it stores]
    retention: [session | persistent | archival]
    schema: [structure of stored data]
```

---

## 8. Tools Required

List all tools the main agent needs access to:

| Tool | Purpose | Permission Level |
|------|---------|------------------|
| [name] | [why needed] | [read/write/execute] |

**Standard tool categories:**
- **File operations**: Read, Write, Edit, Glob, Grep
- **Web access**: WebSearch, WebFetch
- **Execution**: Bash, Scripts
- **Orchestration**: Task (for sub-agents)
- **User interaction**: AskUserQuestion

```yaml
tools:
  allowed:
    - [tool-name]
  denied:
    - [tool-name]  # explicitly block if needed
```

---

## 9. Workflow Diagram

Provide an ASCII diagram showing the flow:

```
User Request
     │
     ▼
[Main Agent]
     │
     ├──► [Sub-Agent 1] ──► [Output 1]
     │
     ├──► [Sub-Agent 2] ──► [Output 2]
     │
     ▼
[Aggregation/Synthesis]
     │
     ▼
Deliverable
```

---

## 10. Error Handling

Define how the agent handles failures:

| Failure Mode | Detection | Recovery |
|--------------|-----------|----------|
| [what can fail] | [how to detect] | [what to do] |

Common failure modes:
- Sub-agent timeout or error
- External API unavailable
- User provides incomplete information
- Budget/constraint violations

---

## 11. Deliverable Specification

For each deliverable from the Agent Case, specify:

| Deliverable | Format | Generated By | Template |
|-------------|--------|--------------|----------|
| [name] | [md/pdf/json/etc] | [main agent or sub-agent] | [template file if any] |

---

## Design Checklist

Before finalizing, verify:

- [ ] Every capability in the Agent Case Description is addressed
- [ ] Every interaction in the Example Session can be handled
- [ ] Every Deliverable has a clear generation path
- [ ] Sub-agents are used for parallelism where beneficial
- [ ] Skills extract reusable knowledge from the system prompt
- [ ] Scripts handle non-deterministic operations
- [ ] MCPs are defined for external integrations
- [ ] Memory captures what needs to persist
- [ ] Error handling covers likely failure modes
- [ ] The design is implementable on multiple harnesses (OAF-compliant)

---

## Example Application

**Input**: Travel Research Agent Case

**Output excerpt**:

```yaml
name: Travel Research Agent
slug: travel-research-agent
version: 0.1.0

sub_agents:
  - name: flight-researcher
    role: researcher
    delegated_tasks:
      - Search for flights matching criteria
      - Compare prices across dates
    tools: [WebSearch, WebFetch]

  - name: hotel-researcher
    role: researcher
    delegated_tasks:
      - Find accommodations in destination
      - Check availability and pricing
    tools: [WebSearch, WebFetch]

  - name: activity-curator
    role: specialist
    delegated_tasks:
      - Research activities suited to travelers
      - Consider weather, interests, mobility
    tools: [WebSearch, WebFetch, Read]

skills:
  - name: travel-planning
    path: skills/travel-planning/
    purpose: Best practices for itinerary creation

  - name: destination-knowledge
    path: skills/destination-knowledge/
    purpose: Country-specific tips, customs, requirements

scripts:
  - name: budget-calculator.py
    purpose: Calculate running totals, currency conversion
    inputs: [items, currency]
    outputs: [breakdown, total]

  - name: date-optimizer.py
    purpose: Find optimal travel dates based on prices/weather
    inputs: [destination, date_range, flexibility]
    outputs: [recommended_dates, reasoning]

memory:
  - label: traveler-preferences
    purpose: Store dietary, mobility, style preferences
    retention: persistent

  - label: past-trips
    purpose: Recall what worked/didn't in previous trips
    retention: archival
```
