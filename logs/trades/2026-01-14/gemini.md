# Trade Execution Log

**Model:** Gemini
**Date:** 2026-01-14

```text

==================================================
📊 ALPACA PRE-FLIGHT STATUS (Gemini)
==================================================
💰 Equity: $990.05
💸 Buying Power: $320.71

📂 Current Positions:
   • LCID: 24 shares @ $11.29 (Current: $10.94)
   • RIOT: 13 shares @ $15.25 (Current: $17.05)
   • UPST: 4 shares @ $50.10 (Current: $46.29)

📝 Open Orders:
   • UPST: STOP SELL 4 shares Stop @ $43.95 (new)

==================================================

📋 Parsing Portfolio Recommendation from Clipboard...
--------------------
📋 CLIPBOARD CONTENT:
ACTION,TICKER,QTY,TYPE,LIMIT_PRICE,STOP_LOSS,TAKE_PROFIT,REASON
SELL,LCID,24,MARKET,N/A,N/A,N/A,Liquidation: Price below 50SMA and fundamental deterioration
SELL,SOUN,19,LIMIT,11.95,N/A,N/A,Adjustment: Lowering target to exit at overhead resistance (50SMA)
HOLD,RIOT,13,N/A,N/A,14.24,N/A,Trend Leader: Holding above 20 & 50 SMA (Trailing Stop updated)
HOLD,UPST,4,N/A,N/A,43.95,N/A,Support Test: Holding unless 50SMA support breaks
BUY,WULF,13,LIMIT,13.65,12.40,16.15,Momentum: Golden Cross setup (TP set to >2R)
--------------------

🔎 Found 5 trade(s) (CSV).

📉 PROCESSING SELL: LCID
   ✅ SELL submitted for LCID

📉 PROCESSING SELL: SOUN
   ✅ Position already closed or doesn't exist for SOUN.

🛡️ SYNCING PROTECTION: RIOT (Target Stop: $14.24)
   ➕ Missing Protection: No stop-loss found for RIOT.
   ✅ SUCCESS: New stop-loss placed for RIOT @ $14.24

🛡️ SYNCING PROTECTION: UPST (Target Stop: $43.95)
   ✅ Already Protected: Existing stop for UPST matches $43.95 (new)

🚀 PROCESSING BUY: WULF
   Order: BUY 13 WULF @ $13.65 (SL: $12.40, TP: $16.15) (Est. Cost: $177.45)
   ✅ SUCCESS: Buy order placed!
```
