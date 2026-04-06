"""
MCP Tool: Stock Technicals & Fundamentals
Source: yfinance (Yahoo Finance — no API key needed, free)
Provides: OHLCV history, SMA-20/50/200, RSI-14, P/E, market cap, sector info.
Fallback: Alpha Vantage for screening (requires API key).
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Tool Definitions
# ─────────────────────────────────────────────

TECHNICALS_TOOL = {
    "name": "get_technicals",
    "description": (
        "Get technical analysis data for a stock or ETF. Returns price history (OHLCV), "
        "moving averages (SMA-20, SMA-50, SMA-200), RSI-14, current price, and 52-week range. "
        "Use this to identify trends, momentum, support/resistance levels, and entry/exit signals."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock or ETF ticker symbol (e.g., 'AAPL', 'SPY')"
            },
            "period": {
                "type": "string",
                "enum": ["1mo", "3mo", "6mo", "1y"],
                "default": "3mo",
                "description": "Historical data period"
            }
        },
        "required": ["ticker"]
    }
}

FUNDAMENTALS_TOOL = {
    "name": "get_fundamentals",
    "description": (
        "Get fundamental financial data for a stock. Returns P/E ratio, EV/EBITDA, "
        "market cap, revenue, earnings, dividend yield, sector, and key valuation metrics. "
        "Use this to evaluate whether a stock is undervalued or overvalued."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol (e.g., 'AAPL')"
            }
        },
        "required": ["ticker"]
    }
}


# ─────────────────────────────────────────────
# Implementations
# ─────────────────────────────────────────────

def get_technicals(ticker: str, period: str = "3mo") -> dict:
    """
    Fetch technical data using yfinance.
    
    Returns:
        {
            "ticker": "AAPL",
            "current_price": 195.50,
            "sma_20": 192.30,
            "sma_50": 188.45,
            "sma_200": 180.20,
            "rsi_14": 58.3,
            "volume_avg": 55000000,
            "week_52_high": 210.40,
            "week_52_low": 155.80,
            "price_history": [{"date": "2026-07-01", "open": ..., "high": ..., "low": ..., "close": ..., "volume": ...}, ...]
        }
    """
    try:
        import yfinance as yf
        import pandas as pd
    except ImportError:
        return {"error": "Install yfinance: pip install yfinance pandas"}

    ticker = ticker.upper().strip()

    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)

        if hist.empty:
            return {"error": f"No data found for {ticker}", "ticker": ticker}

        close = hist["Close"]
        current_price = round(float(close.iloc[-1]), 2)
        volume_avg = int(hist["Volume"].tail(20).mean())

        # Moving averages
        sma_20 = round(float(close.tail(20).mean()), 2) if len(close) >= 20 else None
        sma_50 = round(float(close.tail(50).mean()), 2) if len(close) >= 50 else None
        sma_200 = round(float(close.tail(200).mean()), 2) if len(close) >= 200 else None

        # RSI-14
        rsi = _calculate_rsi(close, 14)

        # 52-week range (use 1y data)
        hist_1y = stock.history(period="1y")
        week_52_high = round(float(hist_1y["High"].max()), 2) if not hist_1y.empty else None
        week_52_low = round(float(hist_1y["Low"].min()), 2) if not hist_1y.empty else None

        # Last 10 days of price history for context
        recent = hist.tail(10)
        price_history = []
        for idx, row in recent.iterrows():
            price_history.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })

        result = {
            "ticker": ticker,
            "current_price": current_price,
            "sma_20": sma_20,
            "sma_50": sma_50,
            "sma_200": sma_200,
            "rsi_14": rsi,
            "volume_avg_20d": volume_avg,
            "week_52_high": week_52_high,
            "week_52_low": week_52_low,
            "price_history_last_10d": price_history,
        }

        # Trend signals
        signals = []
        if sma_20 and sma_50:
            if sma_20 > sma_50:
                signals.append("SMA-20 above SMA-50 (short-term bullish)")
            else:
                signals.append("SMA-20 below SMA-50 (short-term bearish)")
        if rsi:
            if rsi > 70:
                signals.append(f"RSI {rsi:.1f} — OVERBOUGHT")
            elif rsi < 30:
                signals.append(f"RSI {rsi:.1f} — OVERSOLD")
            else:
                signals.append(f"RSI {rsi:.1f} — neutral")
        if current_price and week_52_high:
            pct_from_high = (current_price - week_52_high) / week_52_high * 100
            signals.append(f"{pct_from_high:+.1f}% from 52-week high")

        result["signals"] = signals

        logger.info(f"Technicals {ticker}: ${current_price}, RSI={rsi}, signals={signals}")
        return result

    except Exception as e:
        logger.error(f"Technicals error for {ticker}: {e}")
        return {"error": str(e), "ticker": ticker}


def get_fundamentals(ticker: str) -> dict:
    """
    Fetch fundamental data using yfinance.
    """
    try:
        import yfinance as yf
    except ImportError:
        return {"error": "Install yfinance: pip install yfinance"}

    ticker = ticker.upper().strip()

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or info.get("regularMarketPrice") is None:
            return {"error": f"No fundamental data for {ticker}", "ticker": ticker}

        result = {
            "ticker": ticker,
            "name": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "market_cap": info.get("marketCap"),
            "market_cap_fmt": _format_large_number(info.get("marketCap")),
            "current_price": info.get("regularMarketPrice"),
            
            # Valuation
            "pe_trailing": info.get("trailingPE"),
            "pe_forward": info.get("forwardPE"),
            "peg_ratio": info.get("pegRatio"),
            "ev_ebitda": info.get("enterpriseToEbitda"),
            "price_to_book": info.get("priceToBook"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            
            # Financials
            "revenue_ttm": info.get("totalRevenue"),
            "revenue_fmt": _format_large_number(info.get("totalRevenue")),
            "net_income": info.get("netIncomeToCommon"),
            "profit_margin": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            
            # Dividends
            "dividend_yield": info.get("dividendYield"),
            "payout_ratio": info.get("payoutRatio"),
            
            # Analyst
            "target_mean_price": info.get("targetMeanPrice"),
            "recommendation": info.get("recommendationKey"),
            "num_analysts": info.get("numberOfAnalystOpinions"),
            
            # Risk
            "beta": info.get("beta"),
            "short_ratio": info.get("shortRatio"),
        }

        logger.info(f"Fundamentals {ticker}: P/E={result['pe_trailing']}, MCap={result['market_cap_fmt']}")
        return result

    except Exception as e:
        logger.error(f"Fundamentals error for {ticker}: {e}")
        return {"error": str(e), "ticker": ticker}


def _calculate_rsi(prices, period: int = 14) -> Optional[float]:
    """Calculate RSI-14."""
    try:
        import pandas as pd
        delta = prices.diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        val = float(rsi.iloc[-1])
        return round(val, 1) if not pd.isna(val) else None
    except Exception:
        return None


def _format_large_number(n) -> Optional[str]:
    """Format large numbers: 1500000000 -> '1.5B'"""
    if n is None:
        return None
    n = float(n)
    if abs(n) >= 1e12:
        return f"${n/1e12:.1f}T"
    if abs(n) >= 1e9:
        return f"${n/1e9:.1f}B"
    if abs(n) >= 1e6:
        return f"${n/1e6:.1f}M"
    return f"${n:,.0f}"
