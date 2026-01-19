#!/usr/bin/env python3
"""
itinerary-formatter.py - Generate formatted itinerary document

Inputs:
  - itinerary: structured itinerary data
  - format: [markdown | pdf | html]
  - include_appendix: boolean

Outputs:
  - document: formatted content
  - filename: suggested filename

Dependencies:
  - jinja2, weasyprint (for PDF)
"""

# Requirements: jinja2, weasyprint

import json
from typing import Any
from datetime import datetime


MARKDOWN_TEMPLATE = """# {destination} Itinerary

**Dates:** {start_date} - {end_date}
**Travelers:** {travelers}
**Budget:** {budget}

---

{days}

---

## Budget Summary

| Category | Total |
|----------|-------|
{budget_rows}
| **Grand Total** | **{total}** |
| **Budget** | {budget} |
| **Remaining** | {remaining} |

{appendix}
"""

DAY_TEMPLATE = """## Day {day_num}: {date} - {title}

### Accommodation
- **Hotel:** {hotel_name}
- **Address:** {hotel_address}
- **Cost:** {hotel_cost}

### Activities
{activities}

### Meals
{meals}

### Day Cost: {day_cost}

---

"""

APPENDIX_TEMPLATE = """
## Practical Appendix

### Packing Checklist
{packing_list}

### Key Phrases
{phrases}

### Cultural Tips
{cultural_tips}

### Emergency Contacts
{emergency_contacts}
"""


def format_activities(activities: list) -> str:
    """Format activities list."""
    if not activities:
        return "- Free day\n"

    lines = []
    for act in activities:
        time = act.get("time", "")
        name = act.get("name", "Activity")
        notes = act.get("notes", "")

        line = f"- **{time}** {name}"
        if notes:
            line += f"\n  - {notes}"
        lines.append(line)

    return "\n".join(lines)


def format_meals(meals: list) -> str:
    """Format meals list."""
    if not meals:
        return "- Explore local options\n"

    lines = []
    for meal in meals:
        meal_type = meal.get("type", "Meal")
        restaurant = meal.get("restaurant", "TBD")
        cuisine = meal.get("cuisine", "")
        cost = meal.get("cost", "")

        line = f"- **{meal_type}:** {restaurant}"
        if cuisine:
            line += f" ({cuisine})"
        if cost:
            line += f" - {cost}"
        lines.append(line)

    return "\n".join(lines)


def format_day(day: dict, day_num: int) -> str:
    """Format a single day."""
    return DAY_TEMPLATE.format(
        day_num=day_num,
        date=day.get("date", ""),
        title=day.get("title", f"Day {day_num}"),
        hotel_name=day.get("hotel", {}).get("name", "TBD"),
        hotel_address=day.get("hotel", {}).get("address", "TBD"),
        hotel_cost=day.get("hotel", {}).get("cost", "TBD"),
        activities=format_activities(day.get("activities", [])),
        meals=format_meals(day.get("meals", [])),
        day_cost=day.get("day_cost", "TBD")
    )


def format_appendix(appendix_data: dict) -> str:
    """Format appendix section."""
    packing = "\n".join(f"- [ ] {item}" for item in appendix_data.get("packing", []))
    phrases = "\n".join(f"- **{p['phrase']}** - {p['meaning']}" for p in appendix_data.get("phrases", []))
    tips = "\n".join(f"- {tip}" for tip in appendix_data.get("cultural_tips", []))
    emergency = "\n".join(f"- **{e['type']}:** {e['contact']}" for e in appendix_data.get("emergency", []))

    return APPENDIX_TEMPLATE.format(
        packing_list=packing or "- See packing template",
        phrases=phrases or "- Research key phrases",
        cultural_tips=tips or "- Research local customs",
        emergency_contacts=emergency or "- Research local emergency numbers"
    )


def main(
    itinerary: dict,
    format: str = "markdown",
    include_appendix: bool = True
) -> dict[str, Any]:
    """
    Generate formatted itinerary document.

    Args:
        itinerary: Structured itinerary data
        format: Output format (markdown, pdf, html)
        include_appendix: Whether to include practical appendix

    Returns:
        dict with keys: document, filename
    """
    # Extract itinerary data
    destination = itinerary.get("destination", "Trip")
    start_date = itinerary.get("start_date", "TBD")
    end_date = itinerary.get("end_date", "TBD")
    travelers = itinerary.get("travelers", "TBD")
    budget = itinerary.get("budget", "TBD")
    days = itinerary.get("days", [])
    budget_breakdown = itinerary.get("budget_breakdown", {})
    appendix_data = itinerary.get("appendix", {})

    # Format days
    days_content = ""
    for i, day in enumerate(days, 1):
        days_content += format_day(day, i)

    # Format budget rows
    budget_rows = ""
    total = 0
    for category, amount in budget_breakdown.items():
        budget_rows += f"| {category.title()} | ${amount} |\n"
        total += amount

    # Format appendix
    appendix_content = ""
    if include_appendix:
        appendix_content = format_appendix(appendix_data)

    # Generate document
    document = MARKDOWN_TEMPLATE.format(
        destination=destination,
        start_date=start_date,
        end_date=end_date,
        travelers=travelers,
        budget=budget,
        days=days_content,
        budget_rows=budget_rows,
        total=f"${total}",
        remaining=f"${int(str(budget).replace('$', '').replace(',', '')) - total}" if budget != "TBD" else "TBD",
        appendix=appendix_content
    )

    # Generate filename
    date_str = datetime.now().strftime("%Y%m%d")
    dest_slug = destination.lower().replace(" ", "-")
    filename = f"{dest_slug}-itinerary-{date_str}.md"

    # Convert format if needed
    if format == "html":
        try:
            import markdown
            document = markdown.markdown(document, extensions=['tables'])
            filename = filename.replace(".md", ".html")
        except ImportError:
            pass  # Return markdown if conversion not available

    elif format == "pdf":
        # PDF generation would require weasyprint
        # For now, return markdown with note
        document = f"<!-- PDF conversion requires weasyprint -->\n{document}"
        filename = filename.replace(".md", ".pdf.md")

    return {
        "document": document,
        "filename": filename,
        "format": format
    }


if __name__ == "__main__":
    import sys

    # Example usage
    example_itinerary = {
        "destination": "Japan",
        "start_date": "2024-04-10",
        "end_date": "2024-04-20",
        "travelers": "Family of 4",
        "budget": "$8000",
        "days": [
            {
                "date": "April 10",
                "title": "Arrival in Tokyo",
                "hotel": {"name": "Shibuya Excel", "address": "Shibuya, Tokyo", "cost": "$180"},
                "activities": [
                    {"time": "Evening", "name": "Shibuya Crossing", "notes": "Walk around, get oriented"}
                ],
                "meals": [
                    {"type": "Dinner", "restaurant": "Ichiran Ramen", "cuisine": "Ramen", "cost": "$15/person"}
                ],
                "day_cost": "$240"
            }
        ],
        "budget_breakdown": {
            "accommodation": 1980,
            "transport": 1200,
            "activities": 800,
            "food": 1500
        },
        "appendix": {
            "packing": ["Passport", "Comfortable walking shoes", "Power adapter"],
            "phrases": [
                {"phrase": "Sumimasen", "meaning": "Excuse me"},
                {"phrase": "Arigatou gozaimasu", "meaning": "Thank you very much"}
            ],
            "cultural_tips": ["Remove shoes indoors", "Don't tip", "Be quiet on trains"],
            "emergency": [
                {"type": "Police", "contact": "110"},
                {"type": "Ambulance", "contact": "119"}
            ]
        }
    }

    result = main(itinerary=example_itinerary, format="markdown", include_appendix=True)
    print(result["document"])
