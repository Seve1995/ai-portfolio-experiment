# Trade Execution Log

**Model:** Gemini
**Date:** 2026-01-21

```text

==================================================
📊 ALPACA PRE-FLIGHT STATUS (Gemini)
==================================================
💰 Equity: $1,006.25
💸 Buying Power: $394.68

📂 Current Positions:
   • CORZ: 10 shares @ $18.18 (Current: $18.87)
   • RIOT: 13 shares @ $15.25 (Current: $18.30)
   • UPST: 4 shares @ $50.10 (Current: $46.26)

📝 Open Orders:
   • CORZ: LIMIT SELL 10 shares @ $21.90 (new)
   • CORZ: STOP SELL 10 shares Stop @ $17.50 (OCO-held)
   • RIOT: STOP SELL 13 shares Stop @ $14.80 (new)
   • UPST: STOP SELL 4 shares Stop @ $43.95 (new)

==================================================

📋 Parsing Portfolio Recommendation from Clipboard...
--------------------
📋 CLIPBOARD CONTENT:
ACTION,TICKER,QTY,TYPE,LIMIT_PRICE,STOP_LOSS,TAKE_PROFIT,REASON
HOLD,CORZ,10,N/A,N/A,N/A,N/A,Trend strong maintain existing limit
HOLD,RIOT,13,N/A,N/A,16.50,N/A,Raise trailing stop on AMD news
HOLD,UPST,4,N/A,N/A,43.95,N/A,Maintain hard stop due to weak trend
BUY,CLSK,30,LIMIT,12.85,11.50,15.55,Pre-earnings momentum and squeeze setup
--------------------

🔎 Found 4 trade(s) (CSV).

✋ HOLDING: CORZ (No stop-loss specified)

🛡️ SYNCING PROTECTION: RIOT (Target Stop: $16.50)
   🔄 Updating: Found stop @ $14.80 (new). Replacing with $16.50
   ✅ SUCCESS: Stop-loss update requested for RIOT.

🛡️ SYNCING PROTECTION: UPST (Target Stop: $43.95)
   ✅ Already Protected: Existing stop for UPST matches $43.95 (new)

🚀 PROCESSING BUY: CLSK
   Order: BUY 30 CLSK @ $12.85 (SL: $11.50, TP: $15.55) (Est. Cost: $385.50)
   ✅ SUCCESS: Buy order placed!
```
