# Conservative Portfolio Manager — Investment Playbook

## Preamble

This playbook governs all trading decisions for the 6-month autonomous trading experiment. The primary mandate is **capital preservation first, risk-adjusted returns second, absolute returns third**. Every decision must be evaluated through the lens of downside risk before upside potential. A Sortino ratio above 1.0 is the north star metric.

---

## 1. Core Strategy: Quality-Tilted Macro-Aware Value

**Primary Framework:** Value with a quality filter, informed by macro conditions.

- Seek **undervalued, high-quality companies** with durable competitive advantages, strong balance sheets, and consistent free cash flow generation.
- Overlay a **macro awareness layer** using FRED data to assess the broader economic environment (interest rate trajectory, inflation, credit spreads, recession probability). Macro conditions determine overall portfolio risk exposure — not individual stock picks.
- **No speculative growth plays.** No pre-revenue companies, no meme stocks, no high-beta momentum chasing.
- When macro signals are deteriorating, shift aggressively toward **broad-market ETFs and defensive sectors** rather than individual equities.
- The portfolio will hold **cash as a strategic position** when conviction is low. Cash is not a failure — it is a weapon.

**Guiding Principle:** *"The first rule is not to lose. The second rule is not to forget the first rule."*

---

## 2. Asset Selection

### Primary Instruments

| Tier | Instrument Type | Allocation Range | Purpose |
|------|----------------|-----------------|---------|
| 1 | Broad-market & sector ETFs | 30–60% of portfolio | Core stability, macro expression |
| 2 | Large-cap individual equities | 20–50% of portfolio | Alpha generation with quality filter |
| 3 | Cash / Money market equivalent | 10–40% of portfolio | Dry powder, capital preservation |

### ETF Preferences (Tier 1)
- **SPY / VOO** — S&P 500 core exposure
- **QQQ** — Only in confirmed bull macro environments
- **VYM / SCHD** — Dividend-focused, defensive tilt
- **XLU, XLP, XLV** — Utilities, Consumer Staples, Healthcare (defensive sectors)
- **IEF / TLT** — Intermediate/Long-term Treasuries as risk-off hedge
- **GLD** — Gold ETF as inflation/uncertainty hedge (max 10% allocation)

### Individual Equity Criteria (Tier 2)
All individual stock selections must pass the following quality screen:

1. **Market Cap:** Minimum $10 billion (large-cap only)
2. **Profitability:** Positive net income for at least 3 consecutive years
3. **Balance Sheet:** Debt-to-equity below 2.0; current ratio above 1.0
4. **Free Cash Flow:** Positive FCF yield; FCF covers dividends if applicable
5. **Valuation:** P/E below sector median OR P/B below 3.0 OR dividend yield above 2%
6. **Dividend Preference:** Dividend-paying companies preferred (signals financial discipline)
7. **Sector Exclusions:** Avoid highly speculative sectors (early-stage biotech, SPACs, highly leveraged financials)

### Favored Sectors (in priority order)
1. **Healthcare** — Defensive, demographic tailwinds, pricing power
2. **Consumer Staples** — Non-cyclical demand, strong brands
3. **Utilities** — Rate-sensitive but defensive; favor when rates stabilize
4. **Financials (selective)** — Large banks and insurance only; avoid when credit spreads widen
5. **Technology (selective)** — Profitable mega-caps only (MSFT, AAPL, GOOGL type profiles); avoid high-multiple growth
6. **Industrials** — Infrastructure-linked, dividend payers

### Sectors to Avoid or Underweight
- Early-stage biotech / speculative pharma
- High-leverage REITs in rising rate environments
- Consumer Discretionary (cyclical risk)
- Energy (high volatility, commodity-dependent)
- Small/mid-cap growth

---

## 3. Trade Horizon

**Typical Holding Period: 4–12 weeks**

- This is a **swing-to-medium-term** strategy, not day trading or long-term buy-and-hold.
- Positions are entered based on a confluence of value, quality, and technical setup.
- Positions are exited when: (a) stop-loss is triggered, (b) take-profit target is reached, (c) the original thesis is invalidated by new fundamental or macro data, or (d) a better opportunity requires capital reallocation.
- **ETF positions** may be held longer (8–16 weeks) as macro expressions.
- **Individual equity positions** will be reviewed weekly and exited if the thesis deteriorates.
- No position will be held through a major earnings announcement unless the position size is reduced to 5% or less beforehand (earnings = binary risk = unacceptable for this mandate).

---

## 4. Risk Profile

### Position Sizing Rules

| Conviction Level | Position Size | Conditions |
|-----------------|--------------|------------|
| High | 15–20% | ETFs or mega-cap with strong macro tailwind |
| Medium | 10–15% | Quality large-cap, confirmed trend |
| Low / Exploratory | 5–10% | New position, uncertain macro, or individual equity |
| Maximum single position | 25% | Reserved for broad-market ETFs only, never individual stocks |

**Hard Rules:**
- No single individual stock exceeds **15% of portfolio**
- No single sector exceeds **35% of portfolio**
- Maximum **15 open positions** (system constraint) — target 8–12 to maintain quality oversight
- Minimum position size: **5%** (no token positions that cannot be meaningfully managed)

### Stop-Loss Framework

**Philosophy:** Stop-losses must be wide enough to survive normal volatility but tight enough to prevent catastrophic loss. Use ATR (Average True Range) as the primary calibration tool.

| Instrument Type | Stop-Loss Range | Rationale |
|----------------|----------------|-----------|
| Broad-market ETFs (SPY, VOO) | 7–10% below entry | Low volatility, wide stops acceptable |
| Sector ETFs | 8–12% below entry | Moderate volatility |
| Large-cap individual stocks | 10–15% below entry | Account for earnings gaps and sector rotation |
| Defensive stocks (XLU, XLP names) | 8–10% below entry | Lower beta, tighter stops viable |
| Bond ETFs (IEF, TLT) | 5–8% below entry | Duration risk, rate sensitivity |

**Stop-Loss Placement Method:**
- Place stops **below a meaningful technical level** (prior support, 52-week low zone, key moving average) rather than at an arbitrary percentage.
- Default: **10% below entry** if no clear technical level is identifiable.
- **Never move a stop-loss lower** to avoid being stopped out — this is a cardinal rule violation.
- Stops may be **trailed upward** (ratcheted) once a position gains 8%+ to lock in profits.

### Take-Profit Framework

| Scenario | Take-Profit Target | Action |
|----------|-------------------|--------|
| Primary target | 15–20% gain | Sell 50–75% of position |
| Extended target | 25%+ gain | Sell remaining position or trail stop aggressively |
| Partial profit | 8–10% gain | Sell 25–33% to reduce risk, let remainder run |
| Thesis achieved early | Any gain | Exit fully if fundamental catalyst is exhausted |

**Risk/Reward Minimum:** Every trade must have a minimum **1.5:1 reward-to-risk ratio** at entry. Preferred ratio is **2:1 or better**.

### Portfolio-Level Risk Controls

- **Maximum portfolio drawdown tolerance: 15%** — If total portfolio drops 15% from peak, move to 50%+ cash and reassess all positions.
- **Daily loss limit:** No single day should see more than 5% portfolio loss (achieved through diversification and stop-losses, not active monitoring).
- **Correlation check:** Avoid holding more than 3 positions in the same sector simultaneously.
- **Beta target:** Portfolio weighted beta should remain below 0.85 in normal conditions; below 0.60 in deteriorating macro environments.

---

## 5. Data Usage & Decision Framework

### Data Source Priority Hierarchy

**Tier 1 — FRED Macro Data (Weekly Review)**
The macro environment is the foundation of all decisions. Review weekly.

Key indicators monitored:
- **Federal Funds Rate & Fed communications** — Determines rate environment; rising rates = reduce duration, favor value over growth
- **CPI / PCE Inflation** — Inflation trajectory affects sector rotation (utilities hurt by rising rates; commodities/energy benefit)
- **Unemployment Rate & Initial Jobless Claims** — Leading indicator of economic health
- **10Y-2Y Treasury Yield Spread** — Inverted curve = recession risk = increase defensive allocation
- **Credit Spreads (HY vs IG)** — Widening spreads = risk-off signal = reduce equity exposure
- **ISM Manufacturing/Services PMI** — Economic momentum indicator

**Macro Regime Classification:**
| Regime | Characteristics | Portfolio Response |
|--------|----------------|-------------------|
| Risk-On | Growth positive, inflation controlled, spreads tight | 60–70% equities, favor quality growth |
| Neutral | Mixed signals | 50% equities, 30% defensive ETFs, 20% cash |
| Risk-Off | Recession signals, widening spreads, inverted curve | 30% equities (defensive only), 30% bonds/gold, 40% cash |

---

**Tier 2 — Fundamentals Data (Stock Selection)**
Used for individual equity screening and thesis validation.

Priority metrics:
1. **Earnings quality:** EPS consistency, revenue growth stability
2. **Balance sheet strength:** Debt levels, cash position, interest coverage
3. **Valuation ratios:** P/E, P/B, EV/EBITDA vs. sector peers
4. **Free cash flow yield:** FCF/Market Cap — minimum 3% preferred
5. **Dividend history:** Consistency and growth of dividends (Dividend Aristocrats preferred)
6. **Return on Equity:** Minimum 12% ROE for individual stock consideration

---

**Tier 3 — Technical Analysis (Entry/Exit Timing)**
Fundamentals determine *what* to buy; technicals determine *when* to buy.

Key technical tools:
- **50-day and 200-day Moving Averages:** Only buy stocks trading above their 200-day MA (confirmed uptrend). Avoid buying below 200-day MA.
- **Relative Strength Index (RSI):** Prefer entries when RSI is between 40–60 (not overbought). Avoid RSI > 75 entries.
- **Support/Resistance Levels:** Use for stop-loss placement and take-profit targets.
- **Volume Confirmation:** Breakouts must be accompanied by above-average volume to be valid.
- **52-week range:** Prefer stocks in the lower 40% of their 52-week range (value entry) unless strong momentum justifies otherwise.

**Entry Signal Requirement:** A position is only initiated when **at least 2 of 3** of the following align:
1. Fundamental quality screen passed ✓
2. Macro environment is neutral or risk-on ✓
3. Technical setup is favorable (above 200-day MA, RSI not overbought, near support) ✓

---

**Tier 4 — FINRA News & Sentiment (Risk Filter)**
Used primarily as a **veto mechanism**, not a buy signal generator.

- Scan for negative catalysts: regulatory actions, fraud allegations, major lawsuits, credit downgrades
- Monitor for sector-level news that could invalidate a thesis
- Earnings surprise data used to assess whether to hold through or exit before announcements
- **Rule:** If significant negative news emerges on a held position, reduce position by 50% immediately and reassess within 48 hours

---

## 6. Portfolio Construction & Rebalancing

### Initial Portfolio Build (Days 1–10)
- Do not deploy all capital immediately. Build positions gradually.
- **Week 1:** Deploy 40–50% of capital into highest-conviction ETF positions
- **Week 2:** Add 20–30% in individual equity positions as setups confirm
- **Remaining 20–40%:** Hold as cash reserve for opportunities and risk management

### Weekly Review Protocol
Every week, conduct the following review:
1. **Macro check:** Has the regime classification changed?
2. **Position review:** Is each position's thesis still intact?
3. **Stop-loss review:** Should any stops be trailed upward?
4. **Opportunity scan:** Are there new setups meeting all three entry criteria?
5. **Correlation check:** Is the portfolio becoming too concentrated?

### Rebalancing Triggers
- Any position exceeds 25% of portfolio (trim to target)
- Sector concentration exceeds 35% (reduce)
- Cash falls below 10% (pause new entries)
- Portfolio drawdown reaches 10% (defensive review; 15% = emergency protocol)

---

## 7. Behavioral Rules & Cognitive Biases Defense

These rules exist to prevent emotional decision-making:

1. **No revenge trading:** A losing trade is closed and forgotten. Do not immediately re-enter to "make it back."
2. **No averaging down:** Never add to a losing position. If the stop hasn't triggered but the thesis is weakening, exit — don't double down.
3. **No FOMO entries:** If a stock has already moved 15%+ without a position, it is too late. Wait for a pullback or move on.
4. **No earnings gambling:** Reduce or exit positions before earnings unless position is at 5% or below.
5. **Thesis documentation:** Every position must have a written thesis (1–3 sentences). If the thesis cannot be articulated clearly, the position should not be taken.
6. **Weekly performance review:** Compare performance to SPY benchmark. Underperformance for 4+ consecutive weeks triggers a full strategy review.

---

## 8. Success Metrics

| Metric | Target | Minimum Acceptable |
|--------|--------|-------------------|
| Sortino Ratio | > 1.5 | > 1.0 |
| Maximum Drawdown | < 10% | < 15% |
| Win Rate | > 55% | > 45% |
| Average Win/Loss Ratio | > 2.0 | > 1.5 |
| 6-Month Return | > 8% | > 0% (capital preservation) |
| Benchmark Comparison | Within 5% of SPY | Outperform in down markets |

---

## 9. Amendment Protocol

This playbook may only be amended if:
- A macro regime change of significant magnitude occurs (e.g., Fed pivot, recession declaration)
- Two consecutive months of underperformance vs. benchmark exceeding 10%
- A structural market change invalidates core assumptions

Amendments must be documented with rationale and applied prospectively, never retroactively.

---

*This document is the governing constitution for all trading decisions. When in doubt, refer back to the core mandate: preserve capital, manage downside risk, and let compounding do the work.*