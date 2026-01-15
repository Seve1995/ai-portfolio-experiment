# Trade Execution Log

**Model:** Gemini
**Date:** 2026-01-15

```text

==================================================
📊 ALPACA PRE-FLIGHT STATUS (Gemini)
==================================================
💰 Equity: $999.06
💸 Buying Power: $405.70

📂 Current Positions:
   • RIOT: 13 shares @ $15.25 (Current: $17.14)
   • UPST: 4 shares @ $50.10 (Current: $48.27)

📝 Open Orders:
   • WULF: LIMIT BUY 13 shares @ $13.65 (new)
   • WULF: STOP SELL 13 shares Stop @ $12.40 (OCO-held)
   • WULF: LIMIT SELL 13 shares @ $16.15 (OCO-held)
   • RIOT: STOP SELL 13 shares Stop @ $14.24 (new)
   • UPST: STOP SELL 4 shares Stop @ $43.95 (new)

==================================================

📋 Parsing Portfolio Recommendation from Clipboard...
--------------------
📋 CLIPBOARD CONTENT:
ACTION,TICKER,QTY,TYPE,LIMIT_PRICE,STOP_LOSS,TAKE_PROFIT,REASON
BUY,WULF,13,LIMIT,13.65,12.51,15.93,Top Pick HPC pivot breakout
HOLD,RIOT,13,N/A,N/A,14.24,N/A,Trend Following above 20/50 SMA
HOLD,UPST,4,N/A,N/A,43.95,N/A,Risk Control weak below 20 SMA
--------------------

🔎 Found 3 trade(s) (CSV).

🚀 PROCESSING BUY: WULF
   ⚠️ Pending Order: There is already an active BUY order for WULF. Skipping duplicates.

🛡️ SYNCING PROTECTION: RIOT (Target Stop: $14.24)
   ✅ Already Protected: Existing stop for RIOT matches $14.24 (new)

🛡️ SYNCING PROTECTION: UPST (Target Stop: $43.95)
   ✅ Already Protected: Existing stop for UPST matches $43.95 (new)
```
