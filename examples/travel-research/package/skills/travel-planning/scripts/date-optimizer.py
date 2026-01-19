#!/usr/bin/env python3
"""
date-optimizer.py - Find optimal travel dates based on price/weather/crowds

Inputs:
  - destination: string
  - date_range: {start, end}
  - flexibility_days: number
  - priorities: list of [price | weather | crowds]

Outputs:
  - recommended_dates: {depart, return}
  - reasoning: explanation
  - price_comparison: list of date/price pairs

Dependencies:
  - requests
"""

# Requirements: requests

import json
from typing import Any
from datetime import datetime, timedelta


# Seasonal data for common destinations (simplified)
DESTINATION_DATA = {
    "japan": {
        "peak_months": [3, 4, 10, 11],  # Cherry blossom, fall foliage
        "avoid_months": [8],  # Very hot and humid
        "best_weather": [5, 9, 10],
        "cheapest_months": [1, 2, 6],
        "crowd_level": {
            1: "low", 2: "low", 3: "high", 4: "very_high",
            5: "medium", 6: "low", 7: "medium", 8: "high",
            9: "medium", 10: "high", 11: "high", 12: "medium"
        }
    },
    "europe": {
        "peak_months": [6, 7, 8],
        "avoid_months": [12, 1, 2],
        "best_weather": [5, 6, 9],
        "cheapest_months": [1, 2, 11],
        "crowd_level": {
            1: "low", 2: "low", 3: "medium", 4: "medium",
            5: "medium", 6: "high", 7: "very_high", 8: "very_high",
            9: "medium", 10: "medium", 11: "low", 12: "medium"
        }
    },
    "default": {
        "peak_months": [6, 7, 8, 12],
        "avoid_months": [],
        "best_weather": [4, 5, 9, 10],
        "cheapest_months": [1, 2, 9],
        "crowd_level": {
            1: "low", 2: "low", 3: "medium", 4: "medium",
            5: "medium", 6: "high", 7: "high", 8: "high",
            9: "medium", 10: "medium", 11: "low", 12: "high"
        }
    }
}


def get_destination_data(destination: str) -> dict:
    """Get seasonal data for destination."""
    dest_lower = destination.lower()
    for key in DESTINATION_DATA:
        if key in dest_lower:
            return DESTINATION_DATA[key]
    return DESTINATION_DATA["default"]


def score_date(date: datetime, destination_data: dict, priorities: list) -> tuple[float, list[str]]:
    """Score a date based on priorities."""
    month = date.month
    score = 0.0
    reasons = []

    for priority in priorities:
        if priority == "price":
            if month in destination_data["cheapest_months"]:
                score += 3
                reasons.append("Lower prices this month")
            elif month in destination_data["peak_months"]:
                score -= 2
                reasons.append("Peak season pricing")
            else:
                score += 1

        elif priority == "weather":
            if month in destination_data["best_weather"]:
                score += 3
                reasons.append("Excellent weather expected")
            elif month in destination_data["avoid_months"]:
                score -= 2
                reasons.append("Weather may be challenging")
            else:
                score += 1

        elif priority == "crowds":
            crowd = destination_data["crowd_level"].get(month, "medium")
            if crowd == "low":
                score += 3
                reasons.append("Low tourist crowds")
            elif crowd == "very_high":
                score -= 2
                reasons.append("Very crowded period")
            elif crowd == "high":
                score -= 1
                reasons.append("Higher than average crowds")
            else:
                score += 1

    return score, reasons


def main(
    destination: str,
    date_range: dict,
    flexibility_days: int = 7,
    priorities: list[str] = None
) -> dict[str, Any]:
    """
    Find optimal travel dates based on priorities.

    Args:
        destination: Travel destination
        date_range: Dict with 'start' and 'end' date strings (YYYY-MM-DD)
        flexibility_days: How many days flexible on either side
        priorities: List of priorities: 'price', 'weather', 'crowds'

    Returns:
        dict with keys: recommended_dates, reasoning, price_comparison
    """
    if priorities is None:
        priorities = ["price", "weather", "crowds"]

    dest_data = get_destination_data(destination)

    # Parse date range
    try:
        start = datetime.strptime(date_range["start"], "%Y-%m-%d")
        end = datetime.strptime(date_range["end"], "%Y-%m-%d")
    except (KeyError, ValueError):
        return {
            "error": "Invalid date_range format. Use {start: 'YYYY-MM-DD', end: 'YYYY-MM-DD'}"
        }

    trip_length = (end - start).days

    # Generate candidate departure dates
    candidates = []
    for offset in range(-flexibility_days, flexibility_days + 1):
        candidate_start = start + timedelta(days=offset)
        candidate_end = candidate_start + timedelta(days=trip_length)

        score, reasons = score_date(candidate_start, dest_data, priorities)
        candidates.append({
            "depart": candidate_start.strftime("%Y-%m-%d"),
            "return": candidate_end.strftime("%Y-%m-%d"),
            "score": score,
            "reasons": reasons,
            "offset": offset
        })

    # Sort by score descending
    candidates.sort(key=lambda x: x["score"], reverse=True)

    best = candidates[0]

    # Simulate price comparison (in real impl, would call flight APIs)
    price_comparison = []
    base_price = 1000  # Simulated base price
    for c in candidates[:5]:
        # Adjust price based on score (higher score = lower price assumption)
        estimated_price = base_price - (c["score"] * 50) + (abs(c["offset"]) * 10)
        price_comparison.append({
            "dates": f"{c['depart']} - {c['return']}",
            "estimated_price": f"${max(500, int(estimated_price))}"
        })

    return {
        "recommended_dates": {
            "depart": best["depart"],
            "return": best["return"]
        },
        "reasoning": "; ".join(best["reasons"]) if best["reasons"] else "Standard timing",
        "price_comparison": price_comparison,
        "destination": destination,
        "original_range": date_range
    }


if __name__ == "__main__":
    import sys

    # Example usage
    result = main(
        destination="Japan",
        date_range={"start": "2024-04-10", "end": "2024-04-20"},
        flexibility_days=7,
        priorities=["price", "crowds", "weather"]
    )
    print(json.dumps(result, indent=2))
