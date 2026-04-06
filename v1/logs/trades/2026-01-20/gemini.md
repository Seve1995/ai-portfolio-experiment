# Trade Execution Log

**Model:** Gemini
**Date:** 2026-01-20

```text

==================================================
📊 ALPACA PRE-FLIGHT STATUS (Gemini)
==================================================
💰 Equity: $993.75
💸 Buying Power: $405.72

📂 Current Positions:
   • RIOT: 13 shares @ $15.25 (Current: $17.90)
   • UPST: 4 shares @ $50.10 (Current: $45.90)
   • WULF: 13 shares @ $13.65 (Current: $13.21)

📝 Open Orders:
   • WULF: STOP SELL 13 shares Stop @ $12.70 (OCO-held)
   • RIOT: STOP SELL 13 shares Stop @ $14.80 (new)
   • WULF: LIMIT SELL 13 shares @ $16.15 (new)
   • UPST: STOP SELL 4 shares Stop @ $43.95 (new)

==================================================

📋 Parsing Portfolio Recommendation from Clipboard...
--------------------
📋 CLIPBOARD CONTENT:
ACTION,TICKER,QTY,TYPE,LIMIT_PRICE,STOP_LOSS,TAKE_PROFIT,REASON
CANCEL,WULF,13,N/A,N/A,N/A,N/A,Order stale (>10% from limit)
HOLD,RIOT,13,N/A,N/A,14.80,N/A,Thesis strengthened (AMD deal); trend > 50SMA
HOLD,UPST,4,N/A,N/A,43.95,N/A,Trend > 50SMA; consolidation hold
HOLD,WULF,13,N/A,N/A,13.15,N/A,Trend > 50SMA; establishing technical stop
BUY,CORZ,10,LIMIT,18.95,17.50,21.90,Short Interest 29%; Trend > SMAs; Earnings catalyst Feb 25
--------------------

🔎 Found 5 trade(s) (CSV).

🚫 PROCESSING CANCEL: WULF
   🧹 Cancelling 2 active order(s) for WULF...
   ✅ Cancelled order 75d575a0-6a85-43fa-b589-0dc39ace5eeb
   ✅ Cancelled order 7051868e-2e47-4028-8190-6a857fb4ab27
   ✅ All orders for WULF successfully cancelled.

🛡️ SYNCING PROTECTION: RIOT (Target Stop: $14.80)
   ✅ Already Protected: Existing stop for RIOT matches $14.80 (new)

🛡️ SYNCING PROTECTION: UPST (Target Stop: $43.95)
   ✅ Already Protected: Existing stop for UPST matches $43.95 (new)

🛡️ SYNCING PROTECTION: WULF (Target Stop: $13.15)
   ➕ Missing Protection: No stop-loss found for WULF.
   ✅ SUCCESS: New stop-loss placed for WULF @ $13.15

🚀 PROCESSING BUY: CORZ
   Order: BUY 10 CORZ @ $18.95 (SL: $17.50, TP: $21.90) (Est. Cost: $189.50)
   ✅ SUCCESS: Buy order placed!
```
