"""
MCP Tool: Finnhub Market News
Source: Finnhub API (free tier: 60 calls/minute)
Provides: Market-wide news headlines and ticker-specific news.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"

TOOL_DEFINITION = {
    "name": "get_market_news",
    "description": (
        "Get latest financial news headlines. Can fetch general market news or news specific to a stock ticker. "
        "Use this to identify catalysts, earnings surprises, FDA decisions, M&A activity, or sector-moving events."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker for company-specific news (e.g., 'AAPL'). Omit for general market news."
            },
            "count": {
                "type": "integer",
                "minimum": 3,
                "maximum": 15,
                "default": 8,
                "description": "Number of news items to return"
            }
        },
        "required": []
    }
}


def execute(ticker: Optional[str] = None, count: int = 8) -> dict:
    """
    Fetch market news from Finnhub.
    
    Returns:
        {
            "ticker": "AAPL" or null,
            "news": [
                {
                    "headline": "...",
                    "source": "Reuters",
                    "url": "https://...",
                    "summary": "...",
                    "datetime": "2026-07-01T14:30:00"
                }
            ],
            "count": 8
        }
    """
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        return {"error": "FINNHUB_API_KEY not set. Get one free at https://finnhub.io/register"}

    try:
        with httpx.Client(timeout=10.0) as client:
            if ticker:
                # Company-specific news
                today = datetime.now()
                from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
                to_date = today.strftime("%Y-%m-%d")
                
                response = client.get(
                    f"{FINNHUB_BASE_URL}/company-news",
                    params={
                        "symbol": ticker.upper(),
                        "from": from_date,
                        "to": to_date,
                        "token": api_key,
                    }
                )
            else:
                # General market news
                response = client.get(
                    f"{FINNHUB_BASE_URL}/news",
                    params={
                        "category": "general",
                        "token": api_key,
                    }
                )

            response.raise_for_status()
            data = response.json()

        # Format results
        news = []
        for item in data[:count]:
            dt = item.get("datetime", 0)
            if isinstance(dt, (int, float)):
                dt = datetime.fromtimestamp(dt).strftime("%Y-%m-%dT%H:%M:%S")

            news.append({
                "headline": item.get("headline", ""),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
                "summary": item.get("summary", "")[:300],  # Cap summary length
                "datetime": dt,
            })

        logger.info(f"Finnhub news {'for ' + ticker if ticker else 'general'}: {len(news)} items")

        return {
            "ticker": ticker,
            "news": news,
            "count": len(news),
        }

    except httpx.HTTPStatusError as e:
        return {"error": f"Finnhub API error: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Finnhub error: {e}")
        return {"error": str(e)}
