**CURRENT DATE:** 2026-01-15

**PORTFOLIO STATUS (ALPACA PAPER - ChatGPT):**
- Cash: $427.01
- Equity: $962.69

**MACRO DATA (STANDARDIZED SOURCE):**
- TNX: 4.16 (+0.43% vs prior close)
- DXY: UP (+0.25% vs prior close, source=DX-Y.NYB)

**CURRENT HOLDINGS (STANDARDIZED LAST-CLOSE DATA):**
- APLD: Qty 3 | Entry $35.06 | PnL 2.97% | Last Close Data: LastClose $36.10 | 20SMA $28.69 | 50SMA $28.05 | Trend ABOVE_20&50
- NTLA: Qty 6 | Entry $11.38 | PnL 5.62% | Last Close Data: LastClose $12.02 | 20SMA $9.79 | 50SMA $9.60 | Trend ABOVE_20&50
- NVAX: Qty 14 | Entry $7.44 | PnL 10.08% | Last Close Data: LastClose $8.19 | 20SMA $7.14 | 50SMA $7.01 | Trend ABOVE_20&50
- RXRX: Qty 14 | Entry $4.70 | PnL 3.19% | Last Close Data: LastClose $4.85 | 20SMA $4.45 | 50SMA $4.49 | Trend ABOVE_20&50
- SOUN: Qty 8 | Entry $11.54 | PnL -2.25% | Last Close Data: LastClose $11.28 | 20SMA $10.94 | 50SMA $11.95 | Trend BELOW_50
- UAA: Qty 14 | Entry $5.78 | PnL 0.35% | Last Close Data: LastClose $5.80 | 20SMA $5.09 | 50SMA $4.72 | Trend ABOVE_20&50

**PENDING ORDERS:**
- SELL APLD 3 (LIMIT) Lim: $50.00
- SELL SOUN 8 (STOP) Stop: $10.00
- SELL UAA 14 (STOP) Stop: $4.90
- SELL NVAX 14 (STOP) Stop: $7.00

**ROLE:**
You are a Senior Portfolio Manager running a rules-based experiment.

**GOAL:**
Maximize risk-adjusted return by the experiment end date: March 31, 2026.
Days remaining: 75
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
- Max $risk = $14.44
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
