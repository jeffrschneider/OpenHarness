#!/usr/bin/env python3
"""
briefing-formatter.py - Generate formatted briefing documents

Inputs:
  - prospects: [prospect objects]
  - format: [markdown | pdf | html]
  - include_cheatsheet: boolean

Outputs:
  - document: formatted content
  - cheatsheet: one-liner per prospect

Dependencies:
  - jinja2
"""

# Requirements: jinja2

import json
from typing import Any
from datetime import datetime


PRIORITY_ICONS = {
    1: "⭐",
    2: "⭐",
    3: "",
}

TYPE_ICONS = {
    "followup": "🔄",
    "new": "🆕",
    "priority": "⭐",
    "attention": "⚠️",
}


def format_prospect_section(prospect: dict, rank: int) -> str:
    """Format a single prospect section."""
    is_followup = prospect.get("is_followup", False)
    is_priority = rank <= 2

    # Determine header
    if is_priority and not is_followup:
        header_prefix = "⭐ PRIORITY:"
    elif is_followup:
        header_prefix = "🔄 FOLLOW-UP:"
    else:
        header_prefix = "🆕 NEW:"

    company = prospect.get("company", "Unknown")
    call_time = prospect.get("call_time", "TBD")
    reasoning = prospect.get("reasoning", "")

    lines = [
        f"### {header_prefix} {company} ({call_time})",
        f"*{reasoning}*" if reasoning else "",
        "",
    ]

    # Company snapshot
    company_info = prospect.get("company_info", {})
    lines.extend([
        "**Company Snapshot**",
        f"- **What they do:** {company_info.get('description', 'Research pending')}",
        f"- **Size:** {company_info.get('size', 'Unknown')}",
        f"- **Industry:** {company_info.get('industry', 'Unknown')}",
        "",
    ])

    # Recent developments
    news = prospect.get("recent_news", [])
    if news:
        lines.append("**Recent Developments**")
        for item in news[:3]:
            lines.append(f"- {item.get('date', 'Recent')}: {item.get('title', 'News item')}")
        lines.append("")

    # Key person
    contact_info = prospect.get("contact_info", {})
    contact_name = prospect.get("contact", "Unknown")
    contact_title = contact_info.get("title", "")
    lines.extend([
        f"**Key Person: {contact_name}** ({contact_title})",
        f"- Tenure: {contact_info.get('tenure', 'Unknown')}",
        f"- Background: {contact_info.get('background', 'Research pending')}",
    ])

    mutual = contact_info.get("mutual_connections", [])
    if mutual:
        lines.append(f"- Mutual connections: {', '.join(mutual)}")
    lines.append("")

    # Pain point signals
    signals = prospect.get("signals_detail", [])
    if signals:
        lines.append("**Pain Point Signals**")
        for signal in signals[:3]:
            lines.append(f"- {signal}")
        lines.append("")

    # Follow-up specific section
    if is_followup:
        history = prospect.get("history", {})
        lines.extend([
            "**Conversation History**",
            f"- **Last contact:** {history.get('last_date', 'Unknown')} with {history.get('last_contact', 'Unknown')}",
            f"- **Summary:** {history.get('summary', 'No notes')}",
            f"- **Objection raised:** {history.get('objection', 'None noted')}",
            f"- **What resonated:** {history.get('resonated', 'Unknown')}",
            f"- **Status:** {history.get('status', 'Unknown')}",
            "",
        ])

    # Recommended approach
    approach = prospect.get("approach", {})
    lines.extend([
        "**Recommended Approach**",
        f"- **Angle:** {approach.get('angle', 'Discovery call')}",
        f"- **Opening line:** \"{approach.get('opening_line', 'Standard introduction')}\"",
        "",
        "---",
        "",
    ])

    return "\n".join(lines)


def format_cheatsheet(prospects: list[dict]) -> str:
    """Format quick-reference cheat sheet."""
    lines = [
        "## Quick Reference Cheat Sheet",
        "",
        "| Time | Company | Contact | One-Liner | Priority |",
        "|------|---------|---------|-----------|----------|",
    ]

    for p in prospects:
        icon = "🔄" if p.get("is_followup") else ("⭐" if p.get("priority_rank", 99) <= 2 else "🆕")
        one_liner = p.get("reasoning", "Standard call")[:40]
        lines.append(
            f"| {p.get('call_time', 'TBD')} | {p.get('company', 'Unknown')} | "
            f"{p.get('contact', 'Unknown')} | {one_liner} | {icon} |"
        )

    lines.extend(["", "---", ""])
    return "\n".join(lines)


def main(
    prospects: list[dict],
    format: str = "markdown",
    include_cheatsheet: bool = True
) -> dict[str, Any]:
    """
    Generate formatted briefing document.

    Args:
        prospects: List of researched and ranked prospects
        format: Output format (markdown, pdf, html)
        include_cheatsheet: Whether to include quick reference

    Returns:
        dict with document content and optional cheatsheet
    """
    # Sort by priority rank
    sorted_prospects = sorted(prospects, key=lambda x: x.get("priority_rank", 99))

    # Build document
    lines = [
        "# Sales Call Prep Briefings",
        "",
        f"**Prepared:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Calls:** {len(prospects)} scheduled",
        "",
        "---",
        "",
    ]

    # Add cheatsheet at top if requested
    if include_cheatsheet:
        lines.append(format_cheatsheet(sorted_prospects))

    # Add prospect sections
    lines.append("## Detailed Briefings")
    lines.append("")

    for i, prospect in enumerate(sorted_prospects, 1):
        lines.append(format_prospect_section(prospect, i))

    # Post-call section
    lines.extend([
        "## Post-Call Actions",
        "",
        "After each call, update:",
        "- [ ] CRM notes with conversation summary",
        "- [ ] Objections encountered",
        "- [ ] Next steps agreed",
        "- [ ] Follow-up calendar event",
        "",
    ])

    document = "\n".join(lines)

    # Generate cheatsheet separately
    cheatsheet = format_cheatsheet(sorted_prospects) if include_cheatsheet else ""

    # Handle format conversion
    if format == "html":
        try:
            import markdown
            document = markdown.markdown(document, extensions=['tables'])
        except ImportError:
            pass  # Return markdown if conversion not available
    elif format == "pdf":
        # PDF would require additional libraries
        document = f"<!-- PDF conversion requires weasyprint -->\n{document}"

    # Generate filename
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"sales-prep-{date_str}.{'html' if format == 'html' else 'md'}"

    return {
        "document": document,
        "cheatsheet": cheatsheet,
        "filename": filename,
        "format": format,
        "prospect_count": len(prospects)
    }


if __name__ == "__main__":
    import sys

    # Example usage
    example_prospects = [
        {
            "company": "DataFlow Systems",
            "contact": "Sarah Chen",
            "call_time": "2pm",
            "priority_rank": 1,
            "reasoning": "Just raised $40M Series C, actively hiring for ops roles",
            "is_followup": False,
            "company_info": {
                "description": "Data integration platform for mid-market companies",
                "size": "200 employees",
                "industry": "Technology"
            },
            "contact_info": {
                "title": "VP Operations",
                "tenure": "3 months",
                "background": "Previously at Snowflake",
                "mutual_connections": ["Mike Torres"]
            },
            "signals_detail": [
                "4 job postings for 'data operations'",
                "Series C announced 2 weeks ago"
            ],
            "approach": {
                "angle": "Position as force multiplier for scaling ops team",
                "opening_line": "Congrats on the Series C—saw you're expanding to Europe. How's the team handling the growth?"
            }
        }
    ]

    result = main(prospects=example_prospects, format="markdown", include_cheatsheet=True)
    print(result["document"])
