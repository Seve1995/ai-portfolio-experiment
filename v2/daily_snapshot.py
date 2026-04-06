"""
AI Portfolio Experiment V2 — Daily Snapshot

Pre-fetches shared market data once per day BEFORE running agents.
This ensures all 22 agents see exactly the same data (fairness).

Data collected:
  1. Market indices (SPY, QQQ, IWM, DIA) — OHLCV
  2. Macro indicators (DGS10, VIX, Fed Funds) via FRED
  3. Top market news headlines via Finnhub
  4. Market calendar check (is today a trading day?)

Output: JSON snapshot saved to v2/data/snapshots/{date}.json
"""

import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def is_market_day(check_date: Optional[date] = None) -> bool:
    """Check if a given date is a NYSE trading day."""
    try:
        import pandas_market_calendars as mcal
        nyse = mcal.get_calendar("NYSE")
        if check_date is None:
            check_date = date.today()
        schedule = nyse.schedule(
            start_date=check_date.isoformat(),
            end_date=check_date.isoformat()
        )
        return len(schedule) > 0
    except ImportError:
        logger.warning("pandas_market_calendars not installed, assuming market is open")
        # Fallback: weekdays only
        if check_date is None:
            check_date = date.today()
        return check_date.weekday() < 5


def fetch_index_data() -> dict:
    """Fetch OHLCV data for major market indices/ETFs."""
    try:
        import yfinance as yf
        
        tickers = ["SPY", "QQQ", "IWM", "DIA"]
        result = {}
        
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="5d")
                
                if hist.empty:
                    continue
                    
                latest = hist.iloc[-1]
                prev = hist.iloc[-2] if len(hist) > 1 else latest
                
                daily_change = (float(latest["Close"]) - float(prev["Close"])) / float(prev["Close"])
                
                result[ticker] = {
                    "open": round(float(latest["Open"]), 2),
                    "high": round(float(latest["High"]), 2),
                    "low": round(float(latest["Low"]), 2),
                    "close": round(float(latest["Close"]), 2),
                    "volume": int(latest["Volume"]),
                    "daily_change_pct": round(daily_change * 100, 2),
                }
            except Exception as e:
                logger.error(f"Error fetching {ticker}: {e}")
                
        return result
    except ImportError:
        return {"error": "yfinance not installed"}


def fetch_ohlc_for_tickers(tickers: list[str]) -> dict:
    """
    Fetch today's OHLC data for specific tickers.
    Used by the simulator to check stop-loss/take-profit triggers
    and to execute orders at the open price.
    """
    try:
        import yfinance as yf
        
        result = {}
        if not tickers:
            return result
            
        # Batch download for efficiency
        data = yf.download(tickers, period="2d", progress=False, group_by="ticker")
        
        if data.empty:
            return result
        
        for ticker in tickers:
            try:
                if len(tickers) == 1:
                    ticker_data = data
                else:
                    ticker_data = data[ticker]
                
                if ticker_data.empty or len(ticker_data) < 1:
                    continue
                    
                latest = ticker_data.iloc[-1]
                result[ticker] = {
                    "open": round(float(latest["Open"]), 2),
                    "high": round(float(latest["High"]), 2),
                    "low": round(float(latest["Low"]), 2),
                    "close": round(float(latest["Close"]), 2),
                    "volume": int(latest["Volume"]) if not str(latest["Volume"]) == 'nan' else 0,
                }
            except Exception as e:
                logger.warning(f"OHLC parse error for {ticker}: {e}")
                
        return result
    except ImportError:
        return {"error": "yfinance not installed"}


def build_daily_snapshot(snapshot_date: Optional[date] = None, save_dir: Optional[Path] = None) -> dict:
    """
    Build the complete daily market snapshot.
    
    This runs ONCE per day, before any agents are executed.
    All agents receive identical data from this snapshot.
    
    Returns:
        Complete snapshot dict, also saved to disk.
    """
    if snapshot_date is None:
        snapshot_date = date.today()
    
    logger.info(f"Building daily snapshot for {snapshot_date}")
    
    # 1. Market indices
    logger.info("Fetching market indices...")
    indices = fetch_index_data()
    
    # 2. Macro indicators
    logger.info("Fetching macro data from FRED...")
    try:
        from .mcp_servers.fred_server import execute as fred_execute
        macro = fred_execute(["DGS10", "VIXCLS", "DFF", "T10Y2Y"])
    except Exception as e:
        logger.error(f"FRED error: {e}")
        macro = {"error": str(e)}
    
    # 3. Market news
    logger.info("Fetching market news from Finnhub...")
    try:
        from .mcp_servers.finnhub_news_server import execute as news_execute
        news = news_execute(count=10)
    except Exception as e:
        logger.error(f"Finnhub error: {e}")
        news = {"error": str(e)}
    
    # Build snapshot
    snapshot = {
        "date": snapshot_date.isoformat(),
        "timestamp": datetime.now().isoformat(),
        "is_market_day": is_market_day(snapshot_date),
        "market_indices": indices,
        "macro": macro,
        "news_headlines": news,
    }
    
    # Build market summary for prompt injection
    summary_parts = []
    
    # Index summary
    for idx_name, idx_data in indices.items():
        if isinstance(idx_data, dict) and "close" in idx_data:
            change = idx_data.get("daily_change_pct", 0)
            summary_parts.append(f"{idx_name}: ${idx_data['close']} ({change:+.2f}%)")
    
    # Macro summary
    if isinstance(macro, dict) and "summary" in macro:
        summary_parts.append(macro["summary"])
    
    snapshot["market_summary"] = " | ".join(summary_parts)
    
    # Save to disk
    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
        filepath = save_dir / f"{snapshot_date.isoformat()}.json"
        with open(filepath, "w") as f:
            json.dump(snapshot, f, indent=2, default=str)
        logger.info(f"Snapshot saved to {filepath}")
    
    logger.info(f"Daily snapshot complete: {snapshot['market_summary']}")
    return snapshot


def load_snapshot(snapshot_date: date, data_dir: Path) -> Optional[dict]:
    """Load a previously saved snapshot."""
    filepath = data_dir / f"{snapshot_date.isoformat()}.json"
    if filepath.exists():
        with open(filepath) as f:
            return json.load(f)
    return None
