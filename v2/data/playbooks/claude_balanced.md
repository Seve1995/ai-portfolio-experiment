# Balanced Portfolio Manager — Investment Playbook
### Version 1.0 | Effective: Day 1 of 6-Month Experiment

---

## 1. Core Strategy: Blended Momentum-Quality Approach

**Primary Framework:** A hybrid strategy combining **quality-growth momentum** with **macro-aware sector rotation**.

- **60% Momentum-Quality:** Target stocks with strong price momentum (relative strength) backed by solid fundamentals (earnings growth, healthy balance sheets). Avoid chasing momentum without fundamental support.
- **25% Value/Mean-Reversion:** Opportunistically buy quality companies that have pulled back 15–30% from recent highs without fundamental deterioration. These act as portfolio stabilizers.
- **15% Macro/ETF Overlay:** Use broad ETFs to express macro views (sector rotation, rate sensitivity, risk-on/risk-off) and hedge overall exposure when conditions deteriorate.

**Core Philosophy:** *"Be right on the business, be patient on the price."* Never fight the macro trend. Capital preservation is the first priority; compounding is the second.

---

## 2. Asset Selection

### Stock Selection Criteria

**Quantitative Filters (Must Meet ≥4 of 6):**
1. Market Cap > $2B (mid-to-large cap stability)
2. Revenue growth YoY > 8%
3. EPS growth YoY > 10% OR positive earnings surprise last quarter
4. Price above 50-day AND 200-day moving average (trend confirmation)
5. Relative Strength vs. S&P 500 over 3 months > 0%
6. Debt-to-Equity < 2.0 (financial health)

**Qualitative Filters:**
- Clear competitive moat or market leadership
- No active SEC investigations or major governance red flags
- Catalyst visible within 30–60 days (earnings, product launch, sector tailwind)

### Sector Preferences

| Priority | Sectors | Rationale |
|----------|---------|-----------|
| **Overweight** | Technology, Healthcare, Industrials | Secular growth + pricing power |
| **Neutral** | Consumer Discretionary, Financials, Energy | Cyclical; macro-dependent |
| **Underweight** | Utilities, Real Estate, Consumer Staples | Rate-sensitive; low growth in current environment |

*Sector weights will rotate based on FRED macro signals (yield curve, inflation, employment data).*

### ETF Usage
- **Sector ETFs** (XLK, XLV, XLI, XLE): Express sector views without single-stock risk
- **Broad Market** (SPY, QQQ): Tactical hedges or cash deployment during high-conviction macro periods
- **Max ETF allocation:** 30% of total portfolio at any time

---

## 3. Trade Horizon

| Position Type | Expected Hold Period | % of Portfolio |
|--------------|---------------------|----------------|
| Core Momentum-Quality | 6–12 weeks | 60% |
| Value/Mean-Reversion | 4–8 weeks | 25% |
| Macro/ETF Overlay | 2–6 weeks | 15% |

**General Rules:**
- **Minimum hold:** 5 trading days (avoid noise-driven exits)
- **Maximum hold:** 90 days unless thesis remains intact and position is profitable
- Review all positions weekly; reassess thesis monthly
- Exit immediately if fundamental thesis breaks, regardless of P&L

---

## 4. Risk Profile

### Position Sizing
- **Standard position:** 10–12% of portfolio
- **High-conviction:** Up to 15% (requires 5/6 quantitative filters + strong catalyst)
- **Speculative/ETF overlay:** 5–8%
- **Maximum single position:** 15% (hard cap per system constraints)
- **Maximum open positions:** 12 (leaving buffer below 15-position limit)

### Stop-Loss Framework

| Position Type | Stop-Loss | Rationale |
|--------------|-----------|-----------|
| Momentum-Quality | **-8%** from entry | Momentum breaks quickly; cut fast |
| Value/Mean-Reversion | **-12%** from entry | Needs room to work; wider tolerance |
| ETF/Macro | **-7%** from entry | Liquid; easy to re-enter |

**Stop-Loss Rules:**
- All stops are set at entry — no exceptions
- **Trailing stops:** Once a position gains +15%, trail stop to breakeven
- Once a position gains +20%, trail stop to +8% (lock in partial gains)
- Never widen a stop-loss to "give it more room" — this is a cardinal sin

### Take-Profit Framework

| Scenario | Action |
|----------|--------|
| +15% gain | Trim 30% of position; move stop to breakeven |
| +25% gain | Trim another 30%; trail remaining stop at +12% |
| +40% gain | Evaluate full exit vs. holding with tight +20% trailing stop |
| Thesis achieved early | Exit 100% regardless of time horizon |

### Portfolio-Level Risk Controls
- **Maximum portfolio drawdown trigger:** -12% from peak → reduce all positions by 50%, move to defensive posture
- **Maximum sector concentration:** 30% in any single sector
- **Cash floor:** Maintain minimum 10% cash at all times for opportunistic deployment
- **Correlation check:** Avoid holding >3 highly correlated positions simultaneously

---

## 5. Data Usage & Decision Hierarchy

### Tool Priority Stack

```
PRIORITY 1: FRED Macro Data
PRIORITY 2: Fundamentals
PRIORITY 3: Technicals
PRIORITY 4: FINRA News
```

### FRED Macro Data (Priority 1 — Market Context)
**Used for:** Setting overall risk posture and sector rotation
- **Yield Curve (2Y-10Y spread):** Inverted = defensive tilt; steepening = cyclical opportunity
- **CPI/PCE:** Inflation trajectory drives sector preferences (energy, financials in high inflation)
- **Unemployment Claims:** Leading indicator for consumer/discretionary exposure
- **Fed Funds Rate trajectory:** Determines growth vs. value tilt
- **Decision rule:** If macro environment is deteriorating on ≥2 indicators, reduce gross exposure by 20%

### Fundamentals (Priority 2 — Stock Selection)
**Used for:** Validating momentum signals and identifying value opportunities
- Earnings growth rate and surprise history
- Revenue trajectory and margin trends
- Balance sheet health (debt levels, cash position)
- Forward P/E vs. sector median (avoid paying >2x sector P/E without exceptional growth)
- **Decision rule:** No position initiated without fundamental review

### Technicals (Priority 3 — Entry/Exit Timing)
**Used for:** Optimizing entry points and managing exits
- **Entry signals:** Price above 50-DMA and 200-DMA; RSI 40–65 (not overbought); MACD bullish crossover
- **Exit signals:** Price breaks below 50-DMA on volume; RSI > 75 (overbought); bearish divergence
- **Volume confirmation:** Breakouts require above-average volume to be valid
- **Decision rule:** Even strong fundamental picks wait for technical entry confirmation

### FINRA News (Priority 4 — Risk Filter)
**Used for:** Avoiding landmines and identifying catalysts
- Screen for: Earnings warnings, SEC filings, insider selling patterns, analyst downgrades
- Identify: Upcoming earnings dates, product launches, M&A rumors
- **Decision rule:** Any material negative news = immediate thesis review; do not hold through uncertainty

---

## 6. Weekly Decision Protocol

```
MONDAY:    Review macro data (FRED). Assess market posture.
TUESDAY:   Screen for new opportunities. Review watchlist.
WEDNESDAY: Fundamental deep-dive on top 3 candidates.
THURSDAY:  Technical entry confirmation. Place orders for T+1.
FRIDAY:    Portfolio review. Assess stops. Check news. Plan next week.
```

---

## 7. Behavioral Rules (Non-Negotiable)

1. **No revenge trading:** A loss is information, not an insult. Move on.
2. **No averaging down into losers:** Only add to winning positions.
3. **No FOMO chasing:** If a stock has already moved >20% without me, I missed it. Find the next one.
4. **No earnings gambling:** Do not initiate new positions within 3 days of earnings unless the position is small (<8%) and the thesis is long-term.
5. **Thesis documentation:** Every trade must have a written 2-sentence thesis. If I can't articulate it, I don't take it.
6. **Consistency over brilliance:** A 12% annual return with low drawdowns beats a 30% return followed by a 25% crash.

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| 6-Month Return | > Benchmark (S&P 500) |
| Maximum Drawdown | < 15% |
| Win Rate | > 50% |
| Average Win/Loss Ratio | > 1.5x |
| Sharpe Ratio (estimated) | > 1.0 |

---

*This playbook is a living document in spirit but fixed in execution. Deviations require extraordinary circumstances and explicit acknowledgment. When in doubt, do less, not more.*