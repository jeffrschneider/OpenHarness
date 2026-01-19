# Travel Research Agent - Design

## 1. Agent Identity

```yaml
name: Travel Research Agent
slug: travel-research-agent
version: 0.1.0
description: Plans detailed trips with personalized day-by-day itineraries
tags: [travel, planning, research, personal]
license: MIT
```

## 2. Architecture Overview

The Travel Research Agent uses a **hub-and-spoke architecture** where the main agent coordinates specialized sub-agents that research different aspects of the trip in parallel. This approach enables faster research (flights, hotels, and activities can be researched simultaneously) while keeping each domain isolated (a failed hotel search doesn't block flight research).

The main agent handles user interaction, preference gathering, and final synthesis. It maintains memory of user preferences and past trips to personalize recommendations. When a user requests a trip, the agent first clarifies requirements through conversation, then dispatches sub-agents to research each domain, aggregates their findings, and synthesizes a cohesive itinerary.

Budget tracking runs as a continuous background concern—every recommendation is validated against the budget constraint before being included. The agent uses scripts for precise calculations (currency conversion, running totals, date optimization) rather than relying on LLM math.

## 3. Sub-Agents

| Sub-Agent | Purpose | Inputs | Outputs | Runs In |
|-----------|---------|--------|---------|---------|
| flight-researcher | Find optimal flight options | origin, destination, dates, passengers, budget | ranked flight options with prices | parallel |
| hotel-researcher | Find accommodations | destination, dates, travelers, preferences, budget | ranked hotel options by area | parallel |
| activity-curator | Research things to do | destination, dates, traveler profiles, interests | activities organized by type/day | parallel |
| restaurant-scout | Find dining options | destination, dietary needs, budget tier | restaurant recommendations by area | parallel |
| logistics-planner | Handle transportation & practical details | destination, itinerary draft | transport options, visa info, tips | sequential (after others) |

```yaml
sub_agents:
  - name: flight-researcher
    description: Searches for flights matching travel criteria
    role: researcher
    tools: [WebSearch, WebFetch]
    delegated_tasks:
      - Search for flights on specified dates
      - Compare prices across nearby dates if flexible
      - Identify layover vs direct options
      - Flag budget airlines with baggage restrictions

  - name: hotel-researcher
    description: Finds accommodations matching preferences
    role: researcher
    tools: [WebSearch, WebFetch]
    delegated_tasks:
      - Search hotels/rentals in destination
      - Filter by family-friendly, location, amenities
      - Compare price vs location tradeoffs
      - Note cancellation policies

  - name: activity-curator
    description: Researches activities suited to travelers
    role: specialist
    tools: [WebSearch, WebFetch, Read]
    delegated_tasks:
      - Find activities matching interests and ages
      - Check seasonal availability
      - Note advance booking requirements
      - Balance tourist highlights with local experiences

  - name: restaurant-scout
    description: Finds dining options matching preferences
    role: researcher
    tools: [WebSearch, WebFetch]
    delegated_tasks:
      - Find restaurants near planned activities
      - Filter by dietary restrictions
      - Mix price points within budget
      - Include local specialties

  - name: logistics-planner
    description: Handles practical travel details
    role: specialist
    tools: [WebSearch, WebFetch, Read]
    delegated_tasks:
      - Research visa requirements
      - Plan inter-city transportation
      - Identify travel insurance needs
      - Compile packing recommendations
```

## 4. Skills

| Skill | Purpose | Used By |
|-------|---------|---------|
| travel-planning | Best practices for itinerary structure | main agent |
| destination-japan | Japan-specific knowledge (customs, tips, transit) | all sub-agents |
| family-travel | Considerations for traveling with children | activity-curator, hotel-researcher |
| budget-optimization | Strategies for maximizing value | main agent, all researchers |

```
skills/
  travel-planning/
    SKILL.md              # Itinerary structure, pacing guidelines
    resources/
      itinerary-template.md
      packing-checklist-template.md
    scripts/
      budget-calculator.py
      date-optimizer.py

  destination-japan/
    SKILL.md              # Japan-specific triggers and knowledge
    resources/
      japan-customs.md
      jr-pass-guide.md
      regional-specialties.md
    scripts/
      jpy-converter.py

  family-travel/
    SKILL.md              # Family travel considerations
    resources/
      age-appropriate-activities.md
      family-packing-additions.md

  budget-optimization/
    SKILL.md              # Value maximization strategies
    resources/
      shoulder-season-guide.md
      booking-timing-tips.md
```

## 5. Scripts

| Script | Purpose | Trigger | Language |
|--------|---------|---------|----------|
| budget-calculator.py | Track running totals, validate against limit | After each recommendation | Python |
| date-optimizer.py | Find optimal dates based on price/weather | When dates are flexible | Python |
| jpy-converter.py | Convert JPY to user's currency | When displaying Japan prices | Python |
| itinerary-formatter.py | Generate formatted output document | At completion | Python |

```yaml
scripts:
  - name: budget-calculator.py
    path: skills/travel-planning/scripts/budget-calculator.py
    purpose: Calculate running totals and validate budget
    inputs:
      - items: list of {category, description, amount, currency}
      - budget_limit: number
      - currency: target currency code
    outputs:
      - breakdown: by-category totals
      - total: grand total in target currency
      - remaining: budget remaining
      - over_budget: boolean
    dependencies: [forex-python]

  - name: date-optimizer.py
    path: skills/travel-planning/scripts/date-optimizer.py
    purpose: Find optimal travel dates
    inputs:
      - destination: string
      - date_range: {start, end}
      - flexibility_days: number
      - priorities: [price | weather | crowds]
    outputs:
      - recommended_dates: {depart, return}
      - reasoning: explanation
      - price_comparison: list of date/price pairs
    dependencies: [requests]

  - name: jpy-converter.py
    path: skills/destination-japan/scripts/jpy-converter.py
    purpose: Currency conversion with current rates
    inputs:
      - amount: number
      - from_currency: string (default JPY)
      - to_currency: string
    outputs:
      - converted: number
      - rate: exchange rate used
      - rate_date: when rate was fetched
    dependencies: [forex-python]

  - name: itinerary-formatter.py
    path: skills/travel-planning/scripts/itinerary-formatter.py
    purpose: Generate formatted itinerary document
    inputs:
      - itinerary: structured itinerary data
      - format: [markdown | pdf | html]
      - include_appendix: boolean
    outputs:
      - document: formatted content
      - filename: suggested filename
    dependencies: [jinja2, weasyprint]
```

## 6. MCP Integrations

| MCP Server | Purpose | Tools Exposed | Auth Type |
|------------|---------|---------------|-----------|
| google-calendar | Check user availability, add trip dates | calendar.read, calendar.write | oauth |
| google-maps | Validate locations, get transit directions | maps.directions, maps.places | api-key |

```yaml
mcp_servers:
  - name: google-calendar
    description: Access user's calendar for availability and trip blocking
    protocol: http
    tools:
      - name: calendar.read
        enabled: true
        required: false
        description: Check for conflicts with proposed travel dates
      - name: calendar.write
        enabled: true
        required: false
        description: Block travel dates on calendar
    auth:
      type: oauth
      scopes: [calendar.readonly, calendar.events]

  - name: google-maps
    description: Location validation and transit planning
    protocol: http
    tools:
      - name: maps.directions
        enabled: true
        required: false
        description: Get transit directions between locations
      - name: maps.places
        enabled: true
        required: false
        description: Validate and get details about places
    auth:
      type: api-key
      env_var: GOOGLE_MAPS_API_KEY
```

## 7. Memory Architecture

| Memory Type | Contents | Retention | Used For |
|-------------|----------|-----------|----------|
| traveler-profile | Names, ages, dietary restrictions, mobility needs | persistent | Personalizing all recommendations |
| travel-preferences | Style preferences (pace, luxury level, interests) | persistent | Filtering and ranking options |
| past-trips | Previous destinations, what worked/didn't | archival | Learning from experience |
| current-trip | Working itinerary for active planning session | session | Building the current trip |

```yaml
memory:
  - label: traveler-profile
    purpose: Core information about who is traveling
    retention: persistent
    schema:
      travelers:
        - name: string
          age: number
          dietary: [string]
          mobility: string
          interests: [string]

  - label: travel-preferences
    purpose: How the user likes to travel
    retention: persistent
    schema:
      pace: [relaxed | moderate | packed]
      accommodation: [budget | mid-range | luxury]
      style: [tourist-highlights | off-beaten-path | mixed]
      dislikes: [string]  # e.g., "group tours", "early mornings"

  - label: past-trips
    purpose: Historical trip data for learning
    retention: archival
    schema:
      trips:
        - destination: string
          date: date
          duration: number
          highlights: [string]
          lowlights: [string]
          would_repeat: boolean

  - label: current-trip
    purpose: Working state for active planning
    retention: session
    schema:
      destination: string
      dates: {start: date, end: date}
      budget: {amount: number, currency: string}
      itinerary: [day objects]
      status: [gathering-requirements | researching | drafting | finalizing]
```

## 8. Tools Required

| Tool | Purpose | Permission Level |
|------|---------|------------------|
| WebSearch | Research flights, hotels, activities, restaurants | read |
| WebFetch | Get detailed information from travel sites | read |
| Read | Access skill resources and templates | read |
| Write | Generate itinerary documents | write |
| Task | Dispatch sub-agents | execute |
| AskUserQuestion | Clarify preferences and get decisions | execute |

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
    - Bash  # No need for shell access
    - Edit  # No code editing needed
```

## 9. Workflow Diagram

```
User: "Plan a 10-day trip to Japan"
              │
              ▼
    ┌─────────────────────┐
    │     Main Agent      │
    │ (gather requirements)│
    └─────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   AskUserQuestion   │
    │  (who, when, budget,│
    │   preferences)      │
    └─────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   Dispatch Research │
    │     (parallel)      │
    └─────────────────────┘
              │
    ┌─────────┼─────────┬─────────┬─────────┐
    ▼         ▼         ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│Flight │ │Hotel  │ │Activity│ │Restau-│ │Logis- │
│Research│ │Research│ │Curator│ │rant   │ │tics   │
└───────┘ └───────┘ └───────┘ └───────┘ └───────┘
    │         │         │         │         │
    └─────────┴─────────┴─────────┴─────────┘
              │
              ▼
    ┌─────────────────────┐
    │   Budget Validation │
    │   (run calculator)  │
    └─────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   Synthesize Draft  │
    │   Itinerary         │
    └─────────────────────┘
              │
              ▼
    ┌─────────────────────┐
    │   Present to User   │
    │   (get feedback)    │
    └─────────────────────┘
              │
         ┌────┴────┐
         ▼         ▼
    [Adjustments] [Approved]
         │         │
         └────┬────┘
              ▼
    ┌─────────────────────┐
    │  Format & Deliver   │
    │  (itinerary doc)    │
    └─────────────────────┘
              │
              ▼
        Deliverables
```

## 10. Error Handling

| Failure Mode | Detection | Recovery |
|--------------|-----------|----------|
| Sub-agent timeout | No response within 60s | Retry once, then proceed without that data; inform user |
| No flights found | Empty results from flight-researcher | Suggest alternative dates or nearby airports |
| Over budget | budget-calculator returns over_budget=true | Present options: reduce scope, increase budget, or find alternatives |
| Destination not recognized | WebSearch returns no relevant results | Ask user to clarify or suggest similar destinations |
| User abandons mid-session | No response for extended period | Save current-trip state for later resumption |
| External API down | HTTP errors from WebFetch | Fall back to cached data or alternative sources |

## 11. Deliverable Specification

| Deliverable | Format | Generated By | Template |
|-------------|--------|--------------|----------|
| Day-by-day itinerary | Markdown + PDF | itinerary-formatter.py | itinerary-template.md |
| Budget breakdown | Table in itinerary | budget-calculator.py | (embedded) |
| Packing checklist | Markdown section | main agent | packing-checklist-template.md |
| Pre-trip checklist | Markdown section | logistics-planner | (embedded) |
| Practical appendix | Markdown section | logistics-planner | (embedded) |

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
