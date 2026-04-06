# Trade Execution Log

**Model:** Gemini
**Date:** 2026-01-22

```text

==================================================
📊 ALPACA PRE-FLIGHT STATUS (Gemini)
==================================================
💰 Equity: $987.64
💸 Buying Power: $9.17

📂 Current Positions:
   • CLSK: 30 shares @ $12.85 (Current: $13.07)
   • CORZ: 10 shares @ $18.18 (Current: $17.95)
   • RIOT: 13 shares @ $15.25 (Current: $16.94)
   • UPST: 4 shares @ $50.10 (Current: $46.64)

📝 Open Orders:
   • CLSK: LIMIT SELL 30 shares @ $15.55 (new)
   • CLSK: STOP SELL 30 shares Stop @ $11.50 (OCO-held)
   • RIOT: STOP SELL 13 shares Stop @ $16.50 (new)
   • CORZ: LIMIT SELL 10 shares @ $21.90 (new)
   • CORZ: STOP SELL 10 shares Stop @ $17.50 (OCO-held)
   • UPST: STOP SELL 4 shares Stop @ $43.95 (new)

==================================================

📋 Parsing Portfolio Recommendation from Clipboard...
--------------------
📋 CLIPBOARD CONTENT:
ACTION,TICKER,QTY,TYPE,LIMIT_PRICE,STOP_LOSS,TAKE_PROFIT,REASON
HOLD,CLSK,30,N/A,N/A,11.90,N/A,Trend UP; Stop updated below 20SMA
HOLD,CORZ,10,N/A,N/A,16.25,N/A,Trend UP; Stop updated below 50SMA
HOLD,RIOT,13,N/A,N/A,16.50,N/A,Trend UP; Retaining profit protection stop
HOLD,UPST,4,N/A,N/A,43.95,N/A,Weak Trend; Stop set below 50SMA support
BUY,WULF,15,LIMIT,13.35,12.40,16.25,SI 31% + Tech Uptrend + Mar Earnings Catalyst
--------------------

🔎 Found 5 trade(s) (CSV).

🛡️ SYNCING PROTECTION: CLSK (Target Stop: $11.90)
   🔄 Updating: Found stop @ $11.50 (held). Replacing with $11.90
   ✅ SUCCESS: Stop-loss update requested for CLSK.

🛡️ SYNCING PROTECTION: CORZ (Target Stop: $16.25)
   🔄 Updating: Found stop @ $17.50 (held). Replacing with $16.25
   ✅ SUCCESS: Stop-loss update requested for CORZ.

🛡️ SYNCING PROTECTION: RIOT (Target Stop: $16.50)
   ✅ Already Protected: Existing stop for RIOT matches $16.50 (new)

🛡️ SYNCING PROTECTION: UPST (Target Stop: $43.95)
   ✅ Already Protected: Existing stop for UPST matches $43.95 (new)

🚀 PROCESSING BUY: WULF
   Order: BUY 15 WULF @ $13.35 (SL: $12.40, TP: $16.25) (Est. Cost: $200.25)
   ⚠️ WARNING: Insufficient Buying Power! (Need $200.25, Have $9.17)
```
