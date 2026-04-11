"""
AI Portfolio Experiment V2 — Market Intelligence Hub (MIH) Engine

This engine generates a 150KB institutional-grade daily snapshot (The "MIH")
designed for the 2026 high-rate, AI-volatile regime.

Key features:
1. TOON Formatting (Markdown Tables) for token efficiency.
2. Z-Score & Percentile normalization.
3. RRG Sector Rotation (90-day window).
4. Catalyst Watchlist ($3-$50 universe, 100 tickers).
5. Macro Narrative (Brave Search Summary).
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment
load_dotenv(Path(__file__).parent.parent / ".env")

logger = logging.getLogger(__name__)

# Constants from PRD
WATCHLIST_SIZE = 100
RRG_WINDOW = 90  # 90-day reactive window for 2026 regime
MIN_PRICE = 3.0
MAX_PRICE = 50.0
MIN_VOLUME = 500_000

# RRG - Sector ETFs
SECTOR_ETFS = {
    "Technology": "XLK",
    "Healthcare": "XLV",
    "Discretionary": "XLY",
    "Staples": "XLP",
    "Energy": "XLE",
    "Financials": "XLF",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Utilities": "XLU",
    "Real_Estate": "XLRE",
    "Communication": "XLC"
}
BENCHMARK = "SPY"

# FRED Series
FRED_SERIES = {
    "10Y_Yield": "DGS10",
    "2Y_Yield": "DGS2",
    "Fed_Funds": "DFF",
    "VIX": "VIXCLS",
    "HY_Spread": "BAMLC0A0CM" # ICE BofA US High Yield Index Option-Adjusted Spread
}

# Institutional ETF Holdings Map (Top 5-10 each)
# Used for Dynamic Sector Discovery to remove bias
ETF_HOLDINGS_MAP = {
    "Technology": ["MSFT", "AAPL", "NVDA", "AVGO", "ORCL"],
    "Healthcare": ["UNH", "LLY", "JNJ", "ABBV", "MRK"],
    "Discretionary": ["AMZN", "TSLA", "HD", "MCD", "LOW"],
    "Staples": ["PG", "COST", "PEP", "KO", "PM"],
    "Energy": ["XOM", "CVX", "COP", "EOG", "SLB"],
    "Financials": ["JPM", "V", "MA", "BAC", "WFC"],
    "Industrials": ["GE", "UNP", "HON", "CAT", "RTX"],
    "Materials": ["LIN", "APD", "SHW", "CTVA", "NEM"],
    "Utilities": ["NEE", "SO", "DUK", "CEG", "AEP"],
    "Real_Estate": ["PLD", "AMT", "EQIX", "WELL", "SPG"],
    "Communication": ["META", "GOOGL", "NFLX", "TMUS", "DIS"]
}

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
        if check_date is None:
            check_date = date.today()
        return check_date.weekday() < 5

def fetch_macro_data() -> Dict[str, Any]:
    """Fetch Treasury yields and Credit Spreads from FRED."""
    logger.info("Fetching Macro data from FRED...")
    try:
        from .mcp_servers.fred_server import execute as fred_execute
        series_ids = list(FRED_SERIES.values())
        raw_data = fred_execute(series_ids)
        
        # Map back to readable keys
        # The fred_execute returns a summary and raw dict
        macro_summary = raw_data.get("summary", "No macro summary available.")
        
        # We also want the raw values for our normalization logic later if needed
        # but for Phase 1 we just ensure the fields are extracted
        return {
            "summary": macro_summary,
            "raw": raw_data
        }
    except Exception as e:
        logger.error(f"FRED fetch failed: {e}")
        return {"error": str(e)}

def fetch_market_narrative(snapshot_date: date) -> str:
    """Generate a dense 300-word market briefing via Brave Search."""
    logger.info("Generating Market Narrative via Brave Search...")
    try:
        from .mcp_servers.web_search_server import execute as search_execute
        
        # Multi-query logic for 150KB density
        macro_briefing = ""
        queries = [
            f"detailed US stock market news summary and specific stock catalysts for {snapshot_date.isoformat()}",
            "Federal Reserve 2026 interest rate path sentiment and detailed inflation data analysis",
            "Global geopolitical risks impacts on energy and technology sectors 2026",
            "S&P 500 quantitative analyst outlook and institutional positioning report"
        ]
        
        for q in queries:
            results = search_execute(q, count=10, freshness="pd")
            if "results" in results:
                narrative_parts = [f"### {q.upper()}\n{r['snippet']}" for r in results.get("results", [])]
                macro_briefing += "\n\n" + "\n\n".join(narrative_parts)
        
        briefing = f"INSTITUTIONAL MARKET INTELLIGENCE DOSSIER ({snapshot_date})\n" + macro_briefing
        
        return briefing[:25000] # Cap at ~25k chars for massive context
    except Exception as e:
        logger.error(f"Narrative generation failed: {e}")
        return f"Error generating narrative: {e}"

def fetch_sector_rotation() -> Dict[str, Any]:
    """Calculate RRG Rotation (RS-Ratio and RS-Momentum) for 11 sectors."""
    logger.info(f"Calculating Sector Rotation (RRG) - {RRG_WINDOW}d window...")
    try:
        import yfinance as yf
        all_tickers = list(SECTOR_ETFS.values()) + [BENCHMARK]
        
        # We need historical data for the window + EMA smoothing padding
        data = yf.download(all_tickers, period="6mo", interval="1d", progress=False)
        if data.empty:
            return {"error": "Failed to download Sector ETF data."}
            
        prices = data["Close"]
        benchmark_prices = prices[BENCHMARK]
        
        rotations = {}
        for sector, ticker in SECTOR_ETFS.items():
            if ticker not in prices: continue
            
            # 1. Price Ratio (Relative Strength)
            pr = (prices[ticker] / benchmark_prices).dropna()
            
            # 2. RS-Ratio (using the 90-day window per user PRD)
            # Simplified JdK: 100 * (normalized distance from 90d SMA)
            sma_90 = pr.rolling(window=RRG_WINDOW).mean()
            rs_ratio = 100 * (1 + (pr - sma_90) / sma_90)
            
            # 3. RS-Momentum (Trend of the RS-Ratio)
            # Use a shorter window (10d) to see the rate of change of the ratio
            sma_rs = rs_ratio.rolling(window=10).mean()
            rs_mom = 100 * (1 + (rs_ratio - sma_rs) / sma_rs)
            
            latest_ratio = round(float(rs_ratio.iloc[-1]), 2)
            latest_mom = round(float(rs_mom.iloc[-1]), 2)
            
            # 4. Map to Quadrants
            if latest_ratio >= 100 and latest_mom >= 100:
                quadrant = "LEADING"
            elif latest_ratio >= 100 and latest_mom < 100:
                quadrant = "WEAKENING"
            elif latest_ratio < 100 and latest_mom < 100:
                quadrant = "LAGGING"
            else: # ratio < 100, mom >= 100
                quadrant = "IMPROVING"
                
            rotations[sector] = {
                "ticker": ticker,
                "rs_ratio": latest_ratio,
                "rs_momentum": latest_mom,
                "quadrant": quadrant
            }
            
        return rotations
    except Exception as e:
        logger.error(f"Sector rotation failed: {e}")
        return {"error": str(e)}

def fetch_watchlist_universe() -> List[str]:
    """Discover a broad set of $3-$50 tickers. Uses S&P 600 (Small Cap) as the core hunting ground."""
    logger.info("Scanning for $3-$50 Watchlist Universe...")
    # For now, we use a curated list of high-activity mid/small caps representative of the 2026 regime
    # In a production AI system, this would be a real-time screener.
    core_tickers = [
        "AEHR", "CPRX", "IONQ", "RGTI", "QUBT", "BMEA", "VRTX", "TSLL", "SOXL", "LABU",
        "TNA", "SRTY", "BITO", "MARA", "RIOT", "CLSK", "PLTR", "SOFI", "AFRM", "UPST",
        "CVNA", "CHPT", "BLNK", "BE", "PLUG", "LCID", "HPQ", "MBLY", "RIVN", "QS",
        "HOOD", "COIN", "DKNG", "PENN", "U", "EXEL", "Z", "OPEN", "CPRI", "PTON",
        "RBLX", "SNAP", "DASH", "ABNB", "PATH", "SNOW", "FSLY", "NET", "OKTA", "ZS",
        "MDB", "DDOG", "TEAM", "ASAN", "DOCU", "ZM", "SHOP", "SE", "MELI", "STNE",
        "NU", "PAGS", "ERAS", "IMVT", "FSLR", "ENPH", "RUN", "PLUG", "BE", "BLNK",
        "CELH", "DUOL", "AXON", "GTLB", "CRWD", "PANW", "S", "MSTR", "HOOD", "PYPL",
        "SQ", "MARA", "COIN", "DKNG", "PENN", "SOFI", "AFRM", "UPST", "CVNA", "CHPT",
        "BLNK", "LCID", "RIVN", "QS", "HOOD", "COIN", "DKNG", "PENN", "CPRX", "AEHR",
        "ALNY", "ARWR", "EDIT", "BEAM", "CRSP", "NTLA", "VERV", "BMEA", "BPMC", "KRTX",
        "TSLA", "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "AMD", "INTC", "MU",
        "PYPL", "ABNB", "Airbnb", "SNAP", "DASH", "U", "Unity", "RBLX", "PLTR", "SOFI",
        "AFRM", "UPST", "CVNA", "CHPT", "BLNK", "BE", "PLUG", "LCID", "RIVN", "QS",
        "COIN", "HOOD", "DKNG", "PENN", "PAGS", "STNE", "NU", "SE", "MELI", "SHOP"
    ]
    # We add more dynamically if needed
    return core_tickers

def fetch_dynamic_sector_champions(rotations: Dict[str, Any]) -> List[str]:
    """Identify the top sectors from RRG analysis and return their 'Champion' holdings."""
    logger.info("Identifying Dynamic Sector Champions via RRG Strength...")
    try:
        if "error" in rotations: return []
        
        # Sort sectors by RS_Ratio to find momentum leaders
        sorted_sectors = sorted(
            rotations.items(), 
            key=lambda x: x[1].get("rs_ratio", 0) if isinstance(x[1], dict) else 0, 
            reverse=True
        )
        
        # Take Top 3 Sectors
        top_sectors = [s[0] for s in sorted_sectors[:3]]
        logger.info(f"Top Lead Sectors based on RRG: {top_sectors}")
        
        champions = []
        for sector in top_sectors:
            champions.extend(ETF_HOLDINGS_MAP.get(sector, []))
            
        return list(set(champions))
    except Exception as e:
        logger.error(f"Dynamic discovery failed: {e}")
        return []

def fetch_watchlist_data(tickers: List[str]) -> List[Dict[str, Any]]:
    """Download metrics for the watchlist and filter to the top 100."""
    logger.info(f"Downloading metrics for {len(tickers)} tickers...")
    try:
        import yfinance as yf
        data = yf.download(tickers, period="5d", progress=False)
        if data.empty: return []
        
        closes = data["Close"].iloc[-1]
        volumes = data["Volume"].tail(5).mean()
        
        # Defensive iteration: ensure one bad ticker doesn't crash the loop
        watchlist = []
        for ticker in tickers:
            try:
                # Handle cases where ticker isn't in yfinance result or has NaN
                if ticker not in closes or pd.isna(closes[ticker]) or closes[ticker] == 0:
                    continue
                
                price = round(float(closes[ticker]), 2)
                avg_vol = int(volumes[ticker]) if ticker in volumes and not pd.isna(volumes[ticker]) else 0
                
                if price < MIN_PRICE or price > MAX_PRICE or avg_vol < MIN_VOLUME:
                    continue
                
                watchlist.append({
                    "Tkr": ticker,
                    "Price": price,
                    "Vol_Avg": avg_vol
                })
            except Exception as e:
                # Silently skip if it's just a data-access issue
                continue
            
        return watchlist[:WATCHLIST_SIZE]
    except Exception as e:
        logger.error(f"Watchlist fetch failed: {e}")
        return []

def discover_catalysts(tickers: List[str]) -> Dict[str, str]:
    """Use Brave Search to find high-alpha catalysts. For top 10, do deep extraction."""
    logger.info("Discovering market catalysts (Deep Search extraction)...")
    try:
        from .mcp_servers.web_search_server import execute as search_execute
        
        # 1. Broad Catalyst Search
        query = "high short interest stocks $3-$50 and upcoming FDA PDUFA dates clinical biotech"
        results = search_execute(query, count=10, freshness="pw")
        
        catalysts = {}
        for r in results.get("results", []):
            snippet = r["snippet"].upper()
            # Extract tickers from snippet or context
            for tkr in tickers[:20]: # Only check high-priority ones for broad search
                if tkr in snippet:
                    catalysts[tkr] = r["snippet"][:400] # Inject detailed snippet as 'catalyst'
        
        # 2. Deep Dive for Top 10 High-Volume candidates
        for tkr in tickers[:10]:
            if tkr in catalysts: continue # Skip if already found
            dq = f"{tkr} stock catalyst news earnings FDA trial analysis 2026"
            dr = search_execute(dq, count=3, freshness="pw")
            if "results" in dr and dr["results"]:
                catalysts[tkr] = dr["results"][0]["snippet"] + " " + dr["results"][1]["snippet"]
        
        return catalysts
    except:
        return {}

def compute_technicals(tickers: List[str]) -> Dict[str, Dict[str, Any]]:
    """Download 90d history for watchlist to compute ATR, RVOL, and SMA flags."""
    logger.info(f"Computing Deep Technicals for {len(tickers)} tickers...")
    try:
        import yfinance as yf
        # We need historical data for ATR (14d) and RVOL (20d)
        data = yf.download(tickers, period="6mo", progress=False)
        if data.empty: return {}
        
        tech_data = {}
        for ticker in tickers:
            try:
                hist = data.iloc[:, data.columns.get_level_values(1) == ticker]
                # Flatten the multi-index for this ticker
                hist.columns = hist.columns.get_level_values(0)
                
                if hist.empty or len(hist) < 20: continue
                
                close = hist["Close"]
                high = hist["High"]
                low = hist["Low"]
                vol = hist["Volume"]
                
                # 1. ATR (14-day)
                tr = pd.concat([
                    high - low,
                    (high - close.shift(1)).abs(),
                    (low - close.shift(1)).abs()
                ], axis=1).max(axis=1)
                atr = tr.rolling(window=14).mean().iloc[-1]
                atr_pct = (atr / close.iloc[-1]) * 100
                
                # 2. RVOL (Relative Volume Z-score)
                avg_vol = vol.rolling(window=20).mean()
                std_vol = vol.rolling(window=20).std()
                rvol_z = (vol.iloc[-1] - avg_vol.iloc[-1]) / std_vol.iloc[-1]
                
                # 3. SMA Relationship Flags
                sma_20 = float(close.rolling(window=20).mean().iloc[-1])
                sma_50 = float(close.rolling(window=50).mean().iloc[-1])
                sma_200 = float(close.rolling(window=200).mean().iloc[-1]) if len(close) >= 200 else sma_50
                
                cur_price = float(close.iloc[-1])
                
                # 4. RSI (14-day)
                delta = close.diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs.iloc[-1]))
                
                # ADDING DEEP INSTITUTIONAL ANALYSIS
                dist_20 = round((cur_price - sma_20)/sma_20 * 100, 1)
                dist_50 = round((cur_price - sma_50)/sma_50 * 100, 1)
                dist_200 = round((cur_price - sma_200)/sma_200 * 100, 1)
                
                # Dynamic qualitative summary with deep technical context
                trend = "Constructive Bullish" if cur_price > sma_50 > sma_200 else "Structural Bearish"
                momentum = "Accelerating" if rsi > 50 and dist_20 > 0 else "Decompressing"
                vibe = "Divergent" if (rsi > 60 and cur_price < sma_20) or (rsi < 40 and cur_price > sma_20) else "Aligned"
                
                analysis = (
                    f"{trend} setup. {momentum} on {vibe} volume. "
                    f"Trading {dist_50}% from 50d SMA. RSI {round(rsi, 0)} suggests {vibe} strength. "
                    f"Volatility profile remains in the {round(atr_pct, 1)}% ATR bracket, indicating high-alpha potential."
                )
                
                tech_data[ticker] = {
                    "ATR_Pct": round(float(atr_pct), 2),
                    "RVOL_Z": round(float(rvol_z), 2),
                    "RSI": round(float(rsi), 1),
                    "SMA_20_Dist": dist_20,
                    "SMA_50_Dist": dist_50,
                    "SMA_200_Dist": dist_200,
                    "Bull_Trend": int(cur_price > sma_50 > sma_200),
                    "Analysis": analysis
                }
            except: continue
        return tech_data
    except Exception as e:
        logger.error(f"Technicals calculation failed: {e}")
        return {}

def format_as_toon(watchlist: List[Dict[str, Any]], sectors: Dict[str, Any]) -> str:
    """Serialize the watchlist into a Token-Oriented Markdown Table (TOON)."""
    if not watchlist: return "Watchlist empty."
    
    # Header with extreme density
    cols = ["Tkr", "Price", "RSI", "RVOL_Z", "ATR_Pct", "Volat_Rank", "SMA_20_Dist", "SMA_200_Dist", "Catalyst", "Analysis"]
    header = "| " + " | ".join(cols) + " |"
    divider = "| " + " | ".join(["---"] * len(cols)) + " |"
    
    rows = [header, divider]
    for s in watchlist:
        row_vals = [str(s.get(c, "-")) for c in cols]
        rows.append("| " + " | ".join(row_vals) + " |")
    
    table = "\n".join(rows)
    
    # Also format Sector RRG for rapid parsing
    sector_rows = ["| Sector | Ticker | RS_Ratio | Momentum | Quadrant |", "|---|---|---|---|---|"]
    for name, data in sectors.items():
        row = f"| {name} | {data.get('ticker')} | {data.get('rs_ratio')} | {data.get('rs_momentum')} | **{data.get('quadrant')}** |"
        sector_rows.append(row)
    
    sector_table = "\n".join(sector_rows)
    
    return f"### [MODULE 2: SECTOR ROTATION]\n{sector_table}\n\n### [MODULE 3: CATALYST WATCHLIST]\n{table}"

def build_mih_snapshot(snapshot_date: Optional[date] = None, save_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    The orchestrator for the 150KB Market Intelligence Hub.
    """
    if snapshot_date is None:
        snapshot_date = date.today()
        
    logger.info(f"--- BUILDING MIH SNAPSHOT FOR {snapshot_date} ---")
    
    # 1. Macro & Narrative
    macro = fetch_macro_data()
    narrative = fetch_market_narrative(snapshot_date)
    
    # 2. Sector Rotation (RRG)
    rotation = fetch_sector_rotation()
    
    # 3. Watchlist & Discover Catalysts
    universe = fetch_watchlist_universe()
    
    # NEW: Dynamic Sector Champion discovery (unbiased alpha)
    champions = fetch_dynamic_sector_champions(rotation)
    universe = list(set(universe + champions))
    
    watchlist_raw = fetch_watchlist_data(universe)
    
    # Sort watchlist by volume to prioritize Top 10 for deep catalyst search
    valid_tickers = [s["Tkr"] for s in watchlist_raw]
    catalysts = discover_catalysts(valid_tickers)
    technicals = compute_technicals(valid_tickers)
    
    for stock in watchlist_raw:
        tkr = stock["Tkr"]
        if tkr in technicals:
            stock.update(technicals[tkr])
        stock["Catalyst"] = catalysts.get(tkr, "STABLE")
    
    try:
        df = pd.DataFrame(watchlist_raw)
        if not df.empty and "RVOL_Z" in df and "ATR_Pct" in df:
            df["RVOL_Rank"] = df["RVOL_Z"].rank(pct=True).round(2) * 100
            df["Volat_Rank"] = df["ATR_Pct"].rank(pct=True).round(2) * 100
            watchlist_raw = df.to_dict("records")
    except: pass

    # 5. Serialization (TOON)
    toon_content = format_as_toon(watchlist_raw, rotation)
    
    # Final MIH Payload construction
    snapshot = {
        "metadata": {
            "date": snapshot_date.isoformat(),
            "version": "V2-MIH-2026",
            "is_market_day": is_market_day(snapshot_date)
        },
        "module_1_macro": {
            "narrative": narrative,
            "indicators": macro
        },
        "mih_prompt_payload": f"""# 2026 MARKET INTELLIGENCE HUB (MIH)

## [MODULE 1: MACRO & NARRATIVE]
{narrative}

### GLOBAL INDICATORS (FRED)
{macro.get('summary')}

{toon_content}

## [MODULE 5: SIMULATOR CONSTRAINTS - CODE IS LAW]
- UNIVERSE: Long-only US Equities $3-$50. No Penny Stocks. No Crypto.
- EXECUTION: T+1 Open prices only.
- POSITION SIZING: Max 25% per position ($2,500 on $10k base).
- RISK: Mandatory Stop-Loss (1.5x-2.0x ATR recommended).
"""
    }
    
    # Save logic
    if save_dir:
        save_dir.mkdir(parents=True, exist_ok=True)
        filepath = save_dir / f"{snapshot_date.isoformat()}.json"
        with open(filepath, "w") as f:
            json.dump(snapshot, f, indent=2)
            
    return snapshot


if __name__ == "__main__":
    # Test run
    logging.basicConfig(level=logging.INFO)
    build_mih_snapshot(date(2026, 4, 7), Path("v2/data/snapshots"))
