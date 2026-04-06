"""
MCP Tool: FRED Macro Data
Source: Federal Reserve Economic Data (FRED) API
Provides: DGS10 (10Y Treasury yield), VIXCLS (VIX), DFF (Fed Funds Rate)
Free tier: 120 requests/minute, no daily limit.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy import to avoid startup cost
_fred = None

def _get_fred():
    """Initialize FRED API client."""
    global _fred
    if _fred is None:
        try:
            from fredapi import Fred
            api_key = os.getenv("FRED_API_KEY")
            if not api_key:
                raise ValueError("FRED_API_KEY not set. Get one free at https://fred.stlouisfed.org/docs/api/api_key.html")
            _fred = Fred(api_key=api_key)
        except ImportError:
            raise ImportError("Install fredapi: pip install fredapi")
    return _fred


# ─────────────────────────────────────────────
# Tool Definition (for LLM function calling)
# ─────────────────────────────────────────────

TOOL_DEFINITION = {
    "name": "get_macro",
    "description": (
        "Get current US macroeconomic indicators from the Federal Reserve (FRED). "
        "Returns the latest values for key indicators that affect stock markets: "
        "10-Year Treasury yield, VIX volatility index, and Federal Funds rate. "
        "Use this to assess the macro environment before making trading decisions."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "indicators": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": ["DGS10", "VIXCLS", "DFF", "T10Y2Y", "UNRATE", "CPIAUCSL"]
                },
                "description": (
                    "List of FRED series IDs to fetch. Common ones:\n"
                    "- DGS10: 10-Year Treasury yield (market risk appetite)\n"
                    "- VIXCLS: VIX volatility index (fear gauge)\n"
                    "- DFF: Federal Funds effective rate\n"
                    "- T10Y2Y: 10Y-2Y Treasury spread (recession indicator)\n"
                    "- UNRATE: Unemployment rate\n"
                    "- CPIAUCSL: Consumer Price Index (inflation)"
                ),
                "default": ["DGS10", "VIXCLS", "DFF"]
            }
        },
        "required": []
    }
}

INDICATOR_LABELS = {
    "DGS10": "10-Year Treasury Yield (%)",
    "VIXCLS": "VIX Volatility Index",
    "DFF": "Federal Funds Rate (%)",
    "T10Y2Y": "10Y-2Y Treasury Spread (%)",
    "UNRATE": "Unemployment Rate (%)",
    "CPIAUCSL": "Consumer Price Index",
}


# ─────────────────────────────────────────────
# Tool Implementation
# ─────────────────────────────────────────────

def execute(indicators: Optional[list[str]] = None) -> dict:
    """
    Fetch macro indicators from FRED.
    
    Returns:
        {
            "indicators": {
                "DGS10": {"value": 4.25, "date": "2026-07-01", "label": "10-Year Treasury Yield (%)"},
                ...
            },
            "summary": "10Y yield at 4.25%, VIX at 15.3 (low fear), Fed rate at 5.25%"
        }
    """
    if indicators is None:
        indicators = ["DGS10", "VIXCLS", "DFF"]

    fred = _get_fred()
    results = {}
    summaries = []

    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Look back 30 days for latest data

    for series_id in indicators:
        try:
            data = fred.get_series(series_id, start_date, end_date)
            if data is not None and len(data) > 0:
                # Get the latest non-NaN value
                latest = data.dropna().iloc[-1]
                latest_date = data.dropna().index[-1].strftime("%Y-%m-%d")
                value = round(float(latest), 4)

                label = INDICATOR_LABELS.get(series_id, series_id)
                results[series_id] = {
                    "value": value,
                    "date": latest_date,
                    "label": label,
                }
                summaries.append(f"{label}: {value}")
                logger.info(f"FRED {series_id}: {value} ({latest_date})")
            else:
                results[series_id] = {"value": None, "date": None, "label": INDICATOR_LABELS.get(series_id, series_id), "error": "No data available"}
                logger.warning(f"FRED {series_id}: no data")

        except Exception as e:
            results[series_id] = {"value": None, "error": str(e)}
            logger.error(f"FRED {series_id} error: {e}")

    return {
        "indicators": results,
        "summary": "; ".join(summaries) if summaries else "No data retrieved",
    }
