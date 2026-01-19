#!/usr/bin/env python3
"""
jpy-converter.py - Currency conversion with current rates

Inputs:
  - amount: number
  - from_currency: string (default JPY)
  - to_currency: string

Outputs:
  - converted: number
  - rate: exchange rate used
  - rate_date: when rate was fetched

Dependencies:
  - forex-python (optional)
"""

# Requirements: forex-python

import json
from typing import Any
from datetime import datetime


# Fallback exchange rates (JPY base) - update periodically
# These are approximate rates as of 2024
FALLBACK_RATES_FROM_JPY = {
    "USD": 0.0067,  # 1 JPY = 0.0067 USD (approx 149 JPY/USD)
    "EUR": 0.0062,  # 1 JPY = 0.0062 EUR
    "GBP": 0.0053,  # 1 JPY = 0.0053 GBP
    "AUD": 0.0102,  # 1 JPY = 0.0102 AUD
    "CAD": 0.0091,  # 1 JPY = 0.0091 CAD
    "CHF": 0.0059,  # 1 JPY = 0.0059 CHF
    "CNY": 0.0483,  # 1 JPY = 0.0483 CNY
    "KRW": 8.93,    # 1 JPY = 8.93 KRW
    "SGD": 0.0090,  # 1 JPY = 0.0090 SGD
    "JPY": 1.0,
}

FALLBACK_RATES_TO_JPY = {
    "USD": 149.50,
    "EUR": 162.00,
    "GBP": 189.00,
    "AUD": 98.00,
    "CAD": 110.00,
    "CHF": 169.00,
    "CNY": 20.70,
    "KRW": 0.112,
    "SGD": 111.00,
    "JPY": 1.0,
}


def get_live_rate(from_currency: str, to_currency: str) -> tuple[float, str]:
    """
    Try to get live exchange rate.
    Returns (rate, date_string).
    """
    try:
        from forex_python.converter import CurrencyRates
        c = CurrencyRates()
        rate = c.get_rate(from_currency, to_currency)
        return rate, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except ImportError:
        return None, None
    except Exception:
        return None, None


def get_fallback_rate(from_currency: str, to_currency: str) -> float:
    """Get rate using fallback tables."""
    from_curr = from_currency.upper()
    to_curr = to_currency.upper()

    if from_curr == to_curr:
        return 1.0

    # Convert through JPY as intermediate
    if from_curr == "JPY":
        return FALLBACK_RATES_FROM_JPY.get(to_curr, 1.0)
    elif to_curr == "JPY":
        return FALLBACK_RATES_TO_JPY.get(from_curr, 1.0)
    else:
        # Convert from_currency -> JPY -> to_currency
        to_jpy = FALLBACK_RATES_TO_JPY.get(from_curr, 1.0)
        from_jpy = FALLBACK_RATES_FROM_JPY.get(to_curr, 1.0)
        return to_jpy * from_jpy


def main(
    amount: float,
    from_currency: str = "JPY",
    to_currency: str = "USD"
) -> dict[str, Any]:
    """
    Convert currency amount with current or fallback rates.

    Args:
        amount: Amount to convert
        from_currency: Source currency code (default: JPY)
        to_currency: Target currency code (default: USD)

    Returns:
        dict with keys: converted, rate, rate_date, source
    """
    from_curr = from_currency.upper()
    to_curr = to_currency.upper()

    # Try live rate first
    rate, rate_date = get_live_rate(from_curr, to_curr)

    if rate is not None:
        source = "live"
    else:
        # Use fallback
        rate = get_fallback_rate(from_curr, to_curr)
        rate_date = "2024-01-01 (fallback rates)"
        source = "fallback"

    converted = amount * rate

    return {
        "original": {
            "amount": amount,
            "currency": from_curr
        },
        "converted": round(converted, 2),
        "currency": to_curr,
        "rate": round(rate, 6),
        "rate_date": rate_date,
        "source": source,
        "formatted": f"{amount:,.0f} {from_curr} = {converted:,.2f} {to_curr}"
    }


def batch_convert(amounts: list[dict], to_currency: str = "USD") -> list[dict]:
    """
    Convert multiple amounts.

    Args:
        amounts: List of {amount, currency} dicts
        to_currency: Target currency for all conversions

    Returns:
        List of conversion results
    """
    results = []
    for item in amounts:
        result = main(
            amount=item.get("amount", 0),
            from_currency=item.get("currency", "JPY"),
            to_currency=to_currency
        )
        result["description"] = item.get("description", "")
        results.append(result)
    return results


if __name__ == "__main__":
    import sys

    # Example: Single conversion
    print("Single conversion:")
    result = main(amount=10000, from_currency="JPY", to_currency="USD")
    print(json.dumps(result, indent=2))

    print("\nBatch conversion:")
    # Example: Batch conversion
    items = [
        {"amount": 3200, "currency": "JPY", "description": "teamLab tickets"},
        {"amount": 15000, "currency": "JPY", "description": "Dinner"},
        {"amount": 50000, "currency": "JPY", "description": "JR Pass"},
    ]
    batch_results = batch_convert(items, to_currency="USD")
    for r in batch_results:
        print(f"  {r['description']}: {r['formatted']}")
