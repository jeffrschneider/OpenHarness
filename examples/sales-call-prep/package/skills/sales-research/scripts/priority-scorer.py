#!/usr/bin/env python3
"""
priority-scorer.py - Calculate and rank prospect priorities

Inputs:
  - prospects: [prospect objects with signals]
  - weights: {deal_size, timing, warmth, signals}

Outputs:
  - ranked: [prospects with scores and reasoning]

Dependencies:
  - (none - pure Python)
"""

import json
from typing import Any
from dataclasses import dataclass


# Default scoring weights
DEFAULT_WEIGHTS = {
    "deal_size": 0.25,
    "timing": 0.30,
    "warmth": 0.20,
    "signals": 0.25
}

# Signal score mapping
SIGNAL_SCORES = {
    # High-intent signals
    "recent_funding": 10,
    "leadership_change": 8,
    "job_postings_relevant": 9,
    "expansion_news": 7,
    "competitor_mention": 6,

    # Medium-intent signals
    "general_hiring": 4,
    "industry_event": 3,
    "content_engagement": 3,

    # Relationship signals
    "mutual_connection": 5,
    "previous_contact": 6,
    "referred_lead": 8,

    # Negative signals
    "recent_layoffs": -3,
    "budget_freeze_mentioned": -5,
    "competitor_selected": -7,
}


@dataclass
class ScoredProspect:
    company: str
    contact: str
    call_time: str
    raw_score: float
    normalized_score: int
    priority_rank: int
    score_breakdown: dict
    reasoning: str
    is_followup: bool


def score_deal_size(prospect: dict) -> tuple[float, str]:
    """Score based on estimated deal size."""
    size_indicators = prospect.get("size_indicators", {})

    employee_count = size_indicators.get("employees", 0)
    revenue_estimate = size_indicators.get("revenue", 0)

    # Simple scoring based on company size
    if employee_count > 1000 or revenue_estimate > 100_000_000:
        return 10.0, "Enterprise-scale opportunity"
    elif employee_count > 200 or revenue_estimate > 20_000_000:
        return 7.0, "Mid-market opportunity"
    elif employee_count > 50:
        return 5.0, "SMB opportunity"
    else:
        return 3.0, "Small business"


def score_timing(prospect: dict) -> tuple[float, str]:
    """Score based on timing signals."""
    timing_signals = prospect.get("timing_signals", [])

    score = 5.0  # Base score
    reasons = []

    for signal in timing_signals:
        if signal == "budget_cycle_q4":
            score += 3
            reasons.append("Q4 budget planning")
        elif signal == "contract_expiring":
            score += 4
            reasons.append("Contract expiring soon")
        elif signal == "active_evaluation":
            score += 5
            reasons.append("Actively evaluating")
        elif signal == "just_funded":
            score += 3
            reasons.append("Recently funded")

    return min(score, 10.0), "; ".join(reasons) if reasons else "Standard timing"


def score_warmth(prospect: dict) -> tuple[float, str]:
    """Score based on relationship warmth."""
    relationship = prospect.get("relationship", {})

    if relationship.get("is_followup"):
        last_outcome = relationship.get("last_outcome", "neutral")
        if last_outcome == "positive":
            return 9.0, "Warm follow-up (positive last contact)"
        elif last_outcome == "neutral":
            return 7.0, "Follow-up (neutral last contact)"
        else:
            return 5.0, "Follow-up (needs re-engagement)"

    if relationship.get("referred"):
        return 8.0, "Referred lead"

    if relationship.get("mutual_connections", 0) > 0:
        return 6.0, f"{relationship['mutual_connections']} mutual connections"

    if relationship.get("inbound"):
        return 7.0, "Inbound interest"

    return 4.0, "Cold outreach"


def score_signals(prospect: dict) -> tuple[float, str]:
    """Score based on buying signals detected."""
    signals = prospect.get("signals", [])

    total_score = 0
    signal_reasons = []

    for signal in signals:
        signal_score = SIGNAL_SCORES.get(signal, 0)
        total_score += signal_score
        if signal_score > 0:
            signal_reasons.append(signal.replace("_", " "))

    # Normalize to 0-10 scale
    normalized = min(max(total_score / 2, 0), 10)

    reason = f"Signals: {', '.join(signal_reasons)}" if signal_reasons else "No strong signals"
    return normalized, reason


def calculate_priority_score(
    prospect: dict,
    weights: dict = None
) -> ScoredProspect:
    """Calculate overall priority score for a prospect."""
    weights = weights or DEFAULT_WEIGHTS

    # Calculate component scores
    deal_score, deal_reason = score_deal_size(prospect)
    timing_score, timing_reason = score_timing(prospect)
    warmth_score, warmth_reason = score_warmth(prospect)
    signal_score, signal_reason = score_signals(prospect)

    # Weighted total
    raw_score = (
        deal_score * weights["deal_size"] +
        timing_score * weights["timing"] +
        warmth_score * weights["warmth"] +
        signal_score * weights["signals"]
    )

    # Compile reasoning
    reasons = []
    if timing_score >= 8:
        reasons.append(timing_reason)
    if signal_score >= 7:
        reasons.append(signal_reason)
    if warmth_score >= 7:
        reasons.append(warmth_reason)
    if deal_score >= 8:
        reasons.append(deal_reason)

    return ScoredProspect(
        company=prospect.get("company", "Unknown"),
        contact=prospect.get("contact", "Unknown"),
        call_time=prospect.get("call_time", "Unknown"),
        raw_score=round(raw_score, 2),
        normalized_score=int(raw_score * 10),
        priority_rank=0,  # Will be set after sorting
        score_breakdown={
            "deal_size": {"score": deal_score, "reason": deal_reason},
            "timing": {"score": timing_score, "reason": timing_reason},
            "warmth": {"score": warmth_score, "reason": warmth_reason},
            "signals": {"score": signal_score, "reason": signal_reason}
        },
        reasoning="; ".join(reasons) if reasons else "Standard priority",
        is_followup=prospect.get("relationship", {}).get("is_followup", False)
    )


def main(
    prospects: list[dict],
    weights: dict = None
) -> dict[str, Any]:
    """
    Calculate and rank prospect priorities.

    Args:
        prospects: List of prospect objects with signals
        weights: Optional custom weights for scoring components

    Returns:
        dict with ranked prospects and scoring details
    """
    weights = weights or DEFAULT_WEIGHTS

    # Score all prospects
    scored = [calculate_priority_score(p, weights) for p in prospects]

    # Sort by raw score descending
    scored.sort(key=lambda x: x.raw_score, reverse=True)

    # Assign ranks
    for i, prospect in enumerate(scored, 1):
        prospect.priority_rank = i

    # Convert to dicts for JSON serialization
    ranked = []
    for s in scored:
        ranked.append({
            "company": s.company,
            "contact": s.contact,
            "call_time": s.call_time,
            "priority_rank": s.priority_rank,
            "score": s.normalized_score,
            "reasoning": s.reasoning,
            "is_followup": s.is_followup,
            "breakdown": s.score_breakdown
        })

    return {
        "ranked": ranked,
        "weights_used": weights,
        "total_prospects": len(prospects)
    }


if __name__ == "__main__":
    import sys

    # Example usage
    example_prospects = [
        {
            "company": "DataFlow Systems",
            "contact": "Sarah Chen",
            "call_time": "2pm",
            "size_indicators": {"employees": 200, "revenue": 25_000_000},
            "timing_signals": ["just_funded", "active_evaluation"],
            "signals": ["recent_funding", "job_postings_relevant"],
            "relationship": {"is_followup": False, "mutual_connections": 2}
        },
        {
            "company": "Acme Manufacturing",
            "contact": "Tom Bradley",
            "call_time": "10am",
            "size_indicators": {"employees": 500},
            "timing_signals": ["contract_expiring"],
            "signals": [],
            "relationship": {"is_followup": True, "last_outcome": "neutral"}
        },
        {
            "company": "FirstRate Financial",
            "contact": "Linda Thompson",
            "call_time": "4pm",
            "size_indicators": {"employees": 300},
            "timing_signals": [],
            "signals": [],
            "relationship": {"is_followup": False}
        }
    ]

    result = main(prospects=example_prospects)
    print(json.dumps(result, indent=2))
