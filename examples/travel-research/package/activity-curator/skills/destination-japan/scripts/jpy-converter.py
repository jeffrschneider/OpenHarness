#!/usr/bin/env python3
"""
JPY currency converter for travel budgeting.
"""

import json
import sys
from typing import Dict

# Approximate rates - in production, would fetch live rates
DEFAULT_RATES = {
    "USD": 150.0,
    "EUR": 162.0,
    "GBP": 188.0,
    "AUD": 98.0,
    "CAD": 110.0,
}


def convert_to_jpy(amount: float, from_currency: str, rates: Dict[str, float] = None) -> Dict:
    """Convert foreign currency to JPY."""
    rates = rates or DEFAULT_RATES

    if from_currency == "JPY":
        return {"jpy": amount, "rate": 1.0, "from": from_currency}

    if from_currency not in rates:
        return {"error": f"Unknown currency: {from_currency}"}

    rate = rates[from_currency]
    jpy = amount * rate

    return {
        "jpy": round(jpy),
        "rate": rate,
        "from": from_currency,
        "original": amount
    }


def convert_from_jpy(jpy: float, to_currency: str, rates: Dict[str, float] = None) -> Dict:
    """Convert JPY to foreign currency."""
    rates = rates or DEFAULT_RATES

    if to_currency == "JPY":
        return {"amount": jpy, "rate": 1.0, "to": to_currency}

    if to_currency not in rates:
        return {"error": f"Unknown currency: {to_currency}"}

    rate = rates[to_currency]
    amount = jpy / rate

    return {
        "amount": round(amount, 2),
        "rate": rate,
        "to": to_currency,
        "jpy": jpy
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: jpy-converter.py <json_input>")
        print('To JPY: {"amount": 100, "from": "USD"}')
        print('From JPY: {"jpy": 15000, "to": "USD"}')
        sys.exit(1)

    try:
        data = json.loads(sys.argv[1])

        if "from" in data:
            result = convert_to_jpy(data["amount"], data["from"])
        elif "to" in data:
            result = convert_from_jpy(data["jpy"], data["to"])
        else:
            result = {"error": "Specify 'from' or 'to' currency"}

        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
