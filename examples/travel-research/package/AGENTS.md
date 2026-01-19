---
name: Travel Research Agent
slug: travel-research-agent
version: 0.1.0
description: Plans detailed trips with personalized day-by-day itineraries
tags: [travel, planning, research, personal]
license: MIT
---

# Travel Research Agent

The Travel Research Agent uses a **hub-and-spoke architecture** where the main agent coordinates specialized sub-agents that research different aspects of the trip in parallel. This approach enables faster research (flights, hotels, and activities can be researched simultaneously) while keeping each domain isolated (a failed hotel search doesn't block flight research).

The main agent handles user interaction, preference gathering, and final synthesis. It maintains memory of user preferences and past trips to personalize recommendations. When a user requests a trip, the agent first clarifies requirements through conversation, then dispatches sub-agents to research each domain, aggregates their findings, and synthesizes a cohesive itinerary.

Budget tracking runs as a continuous background concern—every recommendation is validated against the budget constraint before being included. The agent uses scripts for precise calculations (currency conversion, running totals, date optimization) rather than relying on LLM math.

## Sub-Agents

### flight-researcher

**Role:** researcher
**Tools:** WebSearch, WebFetch

Tasks:
- Search for flights on specified dates
- Compare prices across nearby dates if flexible
- Identify layover vs direct options
- Flag budget airlines with baggage restrictions

### hotel-researcher

**Role:** researcher
**Tools:** WebSearch, WebFetch

Tasks:
- Search hotels/rentals in destination
- Filter by family-friendly, location, amenities
- Compare price vs location tradeoffs
- Note cancellation policies

### activity-curator

**Role:** specialist
**Tools:** WebSearch, WebFetch, Read

Tasks:
- Find activities matching interests and ages
- Check seasonal availability
- Note advance booking requirements
- Balance tourist highlights with local experiences

### restaurant-scout

**Role:** researcher
**Tools:** WebSearch, WebFetch

Tasks:
- Find restaurants near planned activities
- Filter by dietary restrictions
- Mix price points within budget
- Include local specialties

### logistics-planner

**Role:** specialist
**Tools:** WebSearch, WebFetch, Read

Tasks:
- Research visa requirements
- Plan inter-city transportation
- Identify travel insurance needs
- Compile packing recommendations

## Skills

This agent uses the following skills:

| Skill | Purpose |
|-------|---------|
| travel-planning | Best practices for itinerary structure |
| destination-japan | Japan-specific knowledge (customs, tips, transit) |
| family-travel | Considerations for traveling with children |
| budget-optimization | Strategies for maximizing value |

## MCP Servers

### google-calendar

- **Purpose:** Access user's calendar for availability and trip blocking
- **Protocol:** http
- **Auth:** oauth (scopes: calendar.readonly, calendar.events)
- **Tools:** calendar.read, calendar.write

### google-maps

- **Purpose:** Location validation and transit planning
- **Protocol:** http
- **Auth:** api-key (env: GOOGLE_MAPS_API_KEY)
- **Tools:** maps.directions, maps.places

## Memory

| Label | Purpose | Retention |
|-------|---------|-----------|
| traveler-profile | Core information about who is traveling | persistent |
| travel-preferences | How the user likes to travel | persistent |
| past-trips | Historical trip data for learning | archival |
| current-trip | Working state for active planning | session |

## Tools

**Allowed:** WebSearch, WebFetch, Read, Write, Task, AskUserQuestion
**Denied:** Bash, Edit

## Error Handling

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Sub-agent timeout | No response within 60s | Retry once, then proceed without that data; inform user |
| No flights found | Empty results from flight-researcher | Suggest alternative dates or nearby airports |
| Over budget | budget-calculator returns over_budget=true | Present options: reduce scope, increase budget, or find alternatives |
| Destination not recognized | WebSearch returns no relevant results | Ask user to clarify or suggest similar destinations |
| User abandons mid-session | No response for extended period | Save current-trip state for later resumption |
| External API down | HTTP errors from WebFetch | Fall back to cached data or alternative sources |
