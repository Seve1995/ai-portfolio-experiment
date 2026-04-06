# Trade Execution Log

**Model:** Gemini
**Date:** 2026-01-12

```text

==================================================
📊 ALPACA PRE-FLIGHT STATUS (Gemini)
==================================================
💰 Equity: $994.30
💸 Buying Power: $599.36

📂 Current Positions:
   • RIOT: 13 shares @ $15.25 (Current: $16.42)
   • UPST: 4 shares @ $50.10 (Current: $45.37)

📝 Open Orders:
   • UPST: STOP SELL 4 shares Stop @ $45.00 (OCO-held)
   • RIOT: STOP SELL 13 shares Stop @ $14.00 (OCO-held)
   • RIOT: LIMIT SELL 13 shares @ $17.55 (new)
   • UPST: LIMIT SELL 4 shares @ $56.30 (new)

==================================================

📋 Parsing Portfolio Recommendation from Clipboard...
--------------------
📋 CLIPBOARD CONTENT:
ACTION,TICKER,QTY,TYPE,LIMIT_PRICE,STOP_LOSS,TAKE_PROFIT,REASON
CANCEL,UPST,4,N/A,N/A,N/A,N/A,Order stale (>10% away from market)
HOLD,RIOT,13,N/A,N/A,14.95,N/A,Trend Bullish (>50SMA); SL below support
HOLD,UPST,4,N/A,N/A,43.95,N/A,Trend Weak but >50SMA; SL below support
BUY,LCID,24,LIMIT,11.35,10.75,12.55,"Trend >20/50SMA, 35% SI, Feb 24 Earns"
--------------------

🔎 Found 4 trade(s) (CSV).

🚫 PROCESSING CANCEL: UPST
   🧹 Cancelling 2 active order(s) for UPST...
   ✅ Cancelled order 4d4ad131-6f17-43d9-b076-3316a95a38ae
   ✅ Cancelled order af0d8cc2-3338-492f-877c-00078a345a11
   ✅ All orders for UPST successfully cancelled.

🛡️ SYNCING PROTECTION: RIOT (Target Stop: $14.95)
   🔄 Updating: Found stop @ $14.00 (held). Replacing with $14.95
   ✅ SUCCESS: Stop-loss update requested for RIOT.

🛡️ SYNCING PROTECTION: UPST (Target Stop: $43.95)
   ➕ Missing Protection: No stop-loss found for UPST.
   ✅ SUCCESS: New stop-loss placed for UPST @ $43.95

🚀 PROCESSING BUY: LCID
   Order: BUY 24 LCID @ $11.35 (SL: $10.75, TP: $12.55) (Est. Cost: $272.40)
   ✅ SUCCESS: Buy order placed!
```
