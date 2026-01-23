"""
Prompt Generator - Refactored for web use
Generates AI prompts without clipboard dependency
"""
import os
import alpaca_trade_api as tradeapi
import yfinance as yf
from datetime import date
import pandas as pd

# Experiment Configuration
EXPERIMENT_END_DATE = date(2026, 3, 31)

# --- Models ---
MODELS = {
    "1": {"name": "ChatGPT", "env_prefix": "CHATGPT"},
    "2": {"name": "Gemini", "env_prefix": "GEMINI"},
    "3": {"name": "Claude", "env_prefix": "CLAUDE"},
    "4": {"name": "Perplexity", "env_prefix": "PERPLEXITY"},
}

def get_alpaca_api(model_key):
    """Returns an Alpaca REST API instance for the selected model."""
    model_info = MODELS.get(model_key)
    if not model_info:
        raise ValueError(f"Invalid model key: {model_key}")
    
    prefix = model_info['env_prefix']
    key = os.getenv(f"{prefix}_ALPACA_KEY")
    secret = os.getenv(f"{prefix}_ALPACA_SECRET")
    
    if not key or not secret:
        key = os.getenv("ALPACA_KEY")
        secret = os.getenv("ALPACA_SECRET")
        
        if not key or not secret:
            raise ValueError(f"No Alpaca API keys found for {model_info['name']}")

    base_url = "https://paper-api.alpaca.markets"
    return tradeapi.REST(key, secret, base_url, api_version="v2"), model_info


def fetch_all_market_data(symbols: list) -> dict:
    """Fetches data for all holdings + Macro tickers in one go."""
    macro_tickers = ["^TNX", "DX-Y.NYB", "UUP"]
    all_tickers = list(set(symbols + macro_tickers))
    
    if not all_tickers:
        return {}

    try:
        data = yf.download(all_tickers, period="6mo", group_by='ticker', threads=True, progress=False)
        return data
    except Exception as e:
        print(f"Batch Download Error: {e}")
        return {}


def get_macro_data(batch_data):
    """Extracts TNX and DXY from the batched data."""
    tnx_str = "TNX: Data Error (Batch failed)"
    dxy_str = "DXY: Data Error (Batch failed)"
    
    # --- TNX ---
    try:
        if isinstance(batch_data.columns, pd.MultiIndex):
            tnx = batch_data["^TNX"]
        else:
            tnx = batch_data if "^TNX" in batch_data.columns else None

        if tnx is not None and not tnx.empty:
            hist = tnx.dropna()
            if len(hist) >= 2:
                prev = float(hist["Close"].iloc[-2])
                last = float(hist["Close"].iloc[-1])
                pct = ((last - prev) / prev) * 100 if prev else 0.0
                tnx_str = f"TNX: {last:.2f} ({pct:+.2f}% vs prior close)"
            else:
                tnx_str = "TNX: Not enough data"
    except Exception as e:
        tnx_str = f"TNX: Data Error ({e})"

    # --- DXY (fallback to UUP) ---
    try:
        dxy = None
        source = "DX-Y.NYB"
        if isinstance(batch_data.columns, pd.MultiIndex):
            if source in batch_data.columns.levels[0]:
                dxy = batch_data[source]
        
        if dxy is None or dxy.empty or len(dxy) < 2:
            source = "UUP"
            if isinstance(batch_data.columns, pd.MultiIndex):
                if source in batch_data.columns.levels[0]:
                    dxy = batch_data[source]

        if dxy is not None and not dxy.empty:
            hist = dxy.dropna()
            if len(hist) >= 2:
                col = "Adj Close" if "Adj Close" in hist.columns else "Close"
                prev = float(hist[col].iloc[-2])
                last = float(hist[col].iloc[-1])
                direction = "UP" if last > prev else ("DOWN" if last < prev else "FLAT")
                pct = ((last - prev) / prev) * 100 if prev else 0.0
                dxy_str = f"DXY: {direction} ({pct:+.2f}% vs prior close, source={source})"
            else:
                dxy_str = f"DXY: Not enough data ({source})"
        else:
            dxy_str = "DXY: Not enough data"
    except Exception as e:
        dxy_str = f"DXY: Data Error ({e})"

    return tnx_str, dxy_str


def get_technical_data(symbol: str, batch_data) -> tuple:
    """Extracts technicals from batched data."""
    try:
        if isinstance(batch_data.columns, pd.MultiIndex):
            if symbol not in batch_data.columns.levels[0]:
                return f"N/A (Symbol {symbol} not in batch)", None
            hist = batch_data[symbol]
        else:
            hist = batch_data

        if hist is None or len(hist) < 55:
            return "N/A (Insufficient history)", None

        closes = hist["Close"].dropna()
        if len(closes) < 55:
            return "N/A (Insufficient close data)", None

        last_close = float(closes.iloc[-1])
        sma_20 = closes.rolling(20).mean().iloc[-1]
        sma_50 = closes.rolling(50).mean().iloc[-1]

        above_20 = last_close > sma_20
        above_50 = last_close > sma_50

        if above_20 and above_50:
            trend = "ABOVE_20&50"
        elif not above_50:
            trend = "BELOW_50"
        else:
            trend = "BELOW_20"

        tech_str = (
            f"LastClose ${last_close:.2f} | "
            f"20SMA ${sma_20:.2f} | "
            f"50SMA ${sma_50:.2f} | "
            f"Trend {trend}"
        )
        return tech_str, last_close
    except Exception as e:
        return f"Data Error ({e})", None


def generate_prompt(model_key: str) -> tuple[str, str]:
    """
    Generates the daily AI prompt for the selected model.
    
    Args:
        model_key: "1" for ChatGPT, "2" for Gemini, "3" for Claude, "4" for Perplexity
    
    Returns:
        Tuple of (prompt_text, status_message)
    """
    try:
        api, model_info = get_alpaca_api(model_key)
    except Exception as e:
        return "", f"❌ API Error: {e}"

    try:
        account = api.get_account()
        positions = api.list_positions()
        orders = api.list_orders(status='open')
    except Exception as e:
        return "", f"❌ Alpaca Error: {e}"

    cash = float(account.cash)
    equity = float(account.equity)
    max_risk = equity * 0.015

    # Fetch All Market Data
    holding_symbols = [p.symbol for p in positions] if positions else []
    batch_data = fetch_all_market_data(holding_symbols)

    # Macro
    tnx_str, dxy_str = get_macro_data(batch_data)

    # Holdings
    holdings_lines = []
    if positions:
        for p in positions:
            tech_str, last_close = get_technical_data(p.symbol, batch_data)
            entry_price = float(p.avg_entry_price)
            if last_close and entry_price > 0:
                pnl = ((last_close - entry_price) / entry_price) * 100
            else:
                pnl = float(p.unrealized_plpc) * 100
            holdings_lines.append(
                f"- {p.symbol}: Qty {p.qty} | Entry ${entry_price:.2f} | "
                f"PnL {pnl:.2f}% | Last Close Data: {tech_str}"
            )
        holdings_txt = "\n".join(holdings_lines)
    else:
        holdings_txt = "No current positions."

    # Pending Orders
    orders_lines = []
    if orders:
        for o in orders:
            details = []
            if o.limit_price: details.append(f"Lim: ${float(o.limit_price):.2f}")
            if o.stop_price: details.append(f"Stop: ${float(o.stop_price):.2f}")
            price_info = " | ".join(details)
            orders_lines.append(
                f"- {o.side.upper()} {o.symbol} {o.qty} ({o.type.upper()}) {price_info}"
            )
        orders_txt = "\n".join(orders_lines)
    else:
        orders_txt = "No pending orders."

    # FINAL PROMPT
    prompt_text = f"""**CURRENT DATE:** {date.today()}

**PORTFOLIO STATUS (ALPACA PAPER - {model_info['name']}):**
- Cash: ${cash:.2f}
- Equity: ${equity:.2f}

**MACRO DATA (STANDARDIZED SOURCE):**
- {tnx_str}
- {dxy_str}

**CURRENT HOLDINGS (STANDARDIZED LAST-CLOSE DATA):**
{holdings_txt}

**PENDING ORDERS:**
{orders_txt}

**ROLE:**
You are a Senior Portfolio Manager running a rules-based experiment.

**GOAL:**
Maximize risk-adjusted return by the experiment end date: {EXPERIMENT_END_DATE.strftime('%B %d, %Y')}.
Days remaining: {(EXPERIMENT_END_DATE - date.today()).days}
Strictly follow all rules. Skip trades if uncertain.

------------------------------------------------------------
## OUTPUT RULES (MANDATORY)
You MUST output exactly TWO sections:
A) DAILY NOTES (bullets, max 8)
B) EXECUTION_TABLE (the ONLY table)
No extra text after the table.

------------------------------------------------------------
## PHASE 0 — PORTFOLIO AUDIT (FIRST PRIORITY)
For EACH holding:
- Use Last Close Data (daily bars only).
- Check overnight news and catalyst validity.

SELL if:
- Major negative news, catalyst invalidated, OR
- Trend shows BELOW_50 AND thesis weakened.

HOLD if not selling:
- You MUST output a HOLD row.
- STOP_LOSS required if a technical invalidation exists, else N/A.
- IMPORTANT: For HOLD positions, do NOT propose TAKE_PROFIT or limit sell orders.
  Risk management for existing holdings is STOP_LOSS ONLY.

------------------------------------------------------------
## PHASE 1 — PENDING ORDER REVIEW
For EACH pending order:
- Evaluate if the order is still valid.

CANCEL if:
- Order is stale (price moved >10% away from limit).
- Thesis invalidated or catalyst passed.
- You are about to SELL the same ticker (existing sell orders are auto-cancelled).

KEEP (do not output) if order is still valid and should remain open.

------------------------------------------------------------
## PHASE 2 — MACRO GATE (NEW BUYS ONLY)
If TNX is up >= +2.00% vs prior close:
- NO NEW BUYS today.
- SELLs, CANCELs, and HOLD stop updates are still allowed.

------------------------------------------------------------
## PHASE 3 — SCANNER (MAX ONE BUY)
Only if Macro allows:

**USE YOUR WEB SEARCH / DEEP RESEARCH CAPABILITY** to find ONE valid setup.

STEP 1 — SEARCH for candidates:
- Use Finviz, MarketWatch, Yahoo Finance, or similar screeners
- Filter: US stocks $3–$50, high short interest (>15%), price above moving averages

STEP 2 — VERIFY each candidate by searching for:
- Current short interest % (cite source: Finviz, NASDAQ, HighShortInterest.com, date)
- Technical levels: confirm price > 20SMA and > 50SMA
- Upcoming catalyst within 30–45 days (earnings, FDA, product launch, etc.)
- No reverse splits, halts, or bankruptcy risk

STEP 3 — VALIDATE setup meets all criteria:

UNIVERSE:
- US-listed common stock
- Price $3–$50
- Tradable on Alpaca
- Avoid reverse splits, halts, bankruptcy risk

SETUP:
- Catalyst in 30–45 days
- Price ABOVE 20SMA and 50SMA
- Short interest > 15% (cite source + date)
- Clear technical stop level

RISK:
- Max $risk = ${max_risk:.2f}
- STOP_LOSS MUST be strictly below LIMIT_PRICE
- Qty = floor(MaxRisk / (Entry − Stop))
- If Qty < 1 → NO BUY

ORDER:
- BUY must be LIMIT
- BUY must include STOP_LOSS and TAKE_PROFIT
- TAKE_PROFIT ≥ 2R
- If search fails or data is uncertain → NO BUY

------------------------------------------------------------
## PHASE 4 — EXECUTION TABLE (STRICT FORMAT)

| ACTION | TICKER | QTY | TYPE | LIMIT_PRICE | STOP_LOSS | TAKE_PROFIT | REASON |
| :--- | :--- | :---: | :--- | :---: | :---: | :---: | :--- |

RULES FOR NUMERIC COLUMNS (STRICT):
1. **QTY**: Must be a clean whole integer.
2. **PRICES** (LIMIT_PRICE, STOP_LOSS, TAKE_PROFIT): Must be RAW NUMBERS ONLY.
3. **NO SYMBOLS**: Do NOT include '$' or ',' in the table.
4. **NO TEXT**: Do NOT add explanatory text (like "@ $7.85") inside numeric columns.
5. **N/A**: Use 'N/A' for any field that is unknown or not applicable.

ACTION VALUES: BUY, SELL, HOLD, CANCEL, NO_TRADES

If no actions are taken, use:
| NO_TRADES | N/A | N/A | N/A | N/A | N/A | N/A | Macro blocked / No valid setups |
"""

    return prompt_text, f"✅ Prompt generated for {model_info['name']}"
