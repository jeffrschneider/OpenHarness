#!/usr/bin/env python3
"""
budget-calculator.py - Calculate running totals and validate budget

Inputs:
  - items: list of {category, description, amount, currency}
  - budget_limit: number
  - currency: target currency code

Outputs:
  - breakdown: by-category totals
  - total: grand total in target currency
  - remaining: budget remaining
  - over_budget: boolean

Dependencies:
  - forex-python (optional, for currency conversion)
"""

# Requirements: forex-python

import json
from typing import Any
from collections import defaultdict


# Fallback exchange rates if forex-python not available
FALLBACK_RATES = {
    "USD": 1.0,
    "EUR": 0.92,
    "GBP": 0.79,
    "JPY": 149.50,
    "AUD": 1.53,
    "CAD": 1.36,
    "CHF": 0.88,
}


def get_exchange_rate(from_currency: str, to_currency: str) -> float:
    """Get exchange rate between currencies."""
    try:
        from forex_python.converter import CurrencyRates
        c = CurrencyRates()
        return c.get_rate(from_currency, to_currency)
    except ImportError:
        # Fallback to hardcoded rates
        if from_currency == to_currency:
            return 1.0
        from_usd = FALLBACK_RATES.get(from_currency, 1.0)
        to_usd = FALLBACK_RATES.get(to_currency, 1.0)
        return to_usd / from_usd
    except Exception:
        return 1.0


def convert_amount(amount: float, from_currency: str, to_currency: str) -> float:
    """Convert amount from one currency to another."""
    if from_currency == to_currency:
        return amount
    rate = get_exchange_rate(from_currency, to_currency)
    return amount * rate


def main(
    items: list[dict],
    budget_limit: float,
    currency: str = "USD"
) -> dict[str, Any]:
    """
    Calculate running totals and validate against budget.

    Args:
        items: List of expense items with category, description, amount, currency
        budget_limit: Maximum budget in target currency
        currency: Target currency code for totals

    Returns:
        dict with keys: breakdown, total, remaining, over_budget
    """
    breakdown = defaultdict(float)
    total = 0.0

    for item in items:
        item_currency = item.get("currency", currency)
        item_amount = item.get("amount", 0)
        category = item.get("category", "misc")

        # Convert to target currency
        converted = convert_amount(item_amount, item_currency, currency)
        breakdown[category] += converted
        total += converted

    remaining = budget_limit - total
    over_budget = total > budget_limit

    return {
        "breakdown": dict(breakdown),
        "total": round(total, 2),
        "remaining": round(remaining, 2),
        "over_budget": over_budget,
        "currency": currency,
        "budget_limit": budget_limit
    }


if __name__ == "__main__":
    import sys

    # Example usage
    example_items = [
        {"category": "accommodation", "description": "Hotel Tokyo", "amount": 180, "currency": "USD"},
        {"category": "accommodation", "description": "Ryokan Kyoto", "amount": 250, "currency": "USD"},
        {"category": "transport", "description": "JR Pass", "amount": 300, "currency": "USD"},
        {"category": "activities", "description": "teamLab", "amount": 3200, "currency": "JPY"},
    ]

    result = main(items=example_items, budget_limit=8000, currency="USD")
    print(json.dumps(result, indent=2))
