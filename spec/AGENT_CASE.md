# Agent Case Specification

A standard format for documenting example agents that can be reproduced across any AI agent platform.

## Purpose

Agent Cases provide platform-agnostic descriptions of useful agents. They focus on **what** the agent does and **how users interact with it**, not **how** it's implemented. This allows:

- Developers to implement the same agent on different harnesses
- Users to understand what to expect from an agent
- Testers to verify an implementation works correctly

## Format

An Agent Case document has three sections:

### 1. Description

What the agent does and the value it provides. This section should:

- Explain the agent's purpose in plain language
- Describe the problem it solves
- List what information or access the agent needs from the user
- Be outcome-focused, not implementation-focused

**Do not** specify implementation details like:
- "Uses web search to find..."
- "Spawns a subagent for..."
- "Stores in memory blocks..."

**Do** describe capabilities in user terms:
- "Researches current prices and availability"
- "Remembers your preferences across sessions"
- "Breaks complex requests into manageable steps"

### 2. Example Session

A realistic conversation showing the complete user journey:

- **Initial trigger**: The user's first message that starts the agent
- **Clarifying questions**: Questions the agent asks to understand the request
- **Progress updates**: How the agent communicates what it's doing
- **User adjustments**: Mid-stream corrections or refinements
- **Completion**: How the agent signals it's done

Format as a dialogue:

```
User: [message]

Agent: [response]

User: [follow-up]

Agent: [response]
```

### 3. Deliverables

What the user receives when the agent completes its work:

- Documents (itinerary, report, briefing)
- Data (spreadsheet, structured list)
- Actions taken (emails sent, files created)
- Summaries or recommendations

---

## Example Agent Cases

See the `/examples/` directory for complete agents with case, design, and package:

- [Travel Research Agent](../examples/travel-research/case/)
- [Sales Call Prep Agent](../examples/sales-call-prep/case/)
