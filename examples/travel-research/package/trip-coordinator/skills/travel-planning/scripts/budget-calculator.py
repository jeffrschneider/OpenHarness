#!/usr/bin/env python3
"""
Budget calculator for travel planning.
Tracks spending across categories and validates against budget constraints.
"""

import json
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class BudgetItem:
    category: str
    description: str
    amount: float
    currency: str = "USD"


@dataclass
class BudgetSummary:
    total_budget: float
    total_spent: float
    remaining: float
    by_category: Dict[str, float]
    over_budget: bool
    warnings: List[str]


def calculate_budget(
    budget: float,
    items: List[Dict],
    category_limits: Optional[Dict[str, float]] = None
) -> BudgetSummary:
    """
    Calculate budget summary from list of items.

    Args:
        budget: Total trip budget
        items: List of {"category": str, "description": str, "amount": float}
        category_limits: Optional per-category limits

    Returns:
        BudgetSummary with totals and warnings
    """
    by_category: Dict[str, float] = {}
    warnings: List[str] = []

    for item in items:
        cat = item["category"]
        amount = item["amount"]
        by_category[cat] = by_category.get(cat, 0) + amount

    total_spent = sum(by_category.values())
    remaining = budget - total_spent
    over_budget = remaining < 0

    if over_budget:
        warnings.append(f"Over budget by ${abs(remaining):.2f}")

    if category_limits:
        for cat, limit in category_limits.items():
            if cat in by_category and by_category[cat] > limit:
                over = by_category[cat] - limit
                warnings.append(f"{cat} over limit by ${over:.2f}")

    if remaining > 0 and remaining < budget * 0.1:
        warnings.append("Less than 10% budget remaining")

    return BudgetSummary(
        total_budget=budget,
        total_spent=total_spent,
        remaining=remaining,
        by_category=by_category,
        over_budget=over_budget,
        warnings=warnings
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: budget-calculator.py <json_input>")
        print('Input: {"budget": 5000, "items": [...], "category_limits": {...}}')
        sys.exit(1)

    try:
        data = json.loads(sys.argv[1])
        result = calculate_budget(
            budget=data["budget"],
            items=data["items"],
            category_limits=data.get("category_limits")
        )
        print(json.dumps(asdict(result), indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
