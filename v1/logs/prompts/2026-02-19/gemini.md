**CURRENT DATE:** 2026-02-19

**PORTFOLIO STATUS (ALPACA PAPER - Gemini):**
- Cash: $648.25
- Equity: $936.25

**MACRO DATA (STANDARDIZED SOURCE):**
- TNX: 4.09 (+0.27% vs prior close)
- DXY: UP (+0.19% vs prior close, source=DX-Y.NYB)

**CURRENT HOLDINGS (STANDARDIZED LAST-CLOSE DATA):**
- GME: Qty 12 | Entry $24.88 | PnL -3.53% | Last Close Data: LastClose $24.00 | 20SMA $24.08 | 50SMA $22.54 | Trend BELOW_20

**PENDING ORDERS:**
- SELL GME 12 (STOP) Stop: $22.10

**ROLE:**
You are a Senior Portfolio Manager running a rules-based experiment.

**GOAL:**
Maximize risk-adjusted return by the experiment end date: March 31, 2026.
Days remaining: 40
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
- Max $risk = $14.04
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
