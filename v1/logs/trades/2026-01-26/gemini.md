# Trade Execution Log

**Model:** Gemini
**Date:** 2026-01-26

```text

==================================================
📊 ALPACA PRE-FLIGHT STATUS (Gemini)
==================================================
💰 Equity: $1,011.00
💸 Buying Power: $9.17

📂 Current Positions:
   • CLSK: 30 shares @ $12.85 (Current: $13.54)
   • CORZ: 10 shares @ $18.18 (Current: $19.30)
   • RIOT: 13 shares @ $15.25 (Current: $17.17)
   • UPST: 4 shares @ $50.10 (Current: $44.85)

📝 Open Orders:
   • CORZ: STOP SELL 10 shares Stop @ $15.95 (OCO-held)
   • CLSK: STOP SELL 30 shares Stop @ $12.25 (OCO-held)
   • CLSK: LIMIT SELL 30 shares @ $15.55 (new)
   • RIOT: STOP SELL 13 shares Stop @ $16.50 (new)
   • CORZ: LIMIT SELL 10 shares @ $21.90 (new)
   • UPST: STOP SELL 4 shares Stop @ $43.95 (new)

==================================================

📋 Parsing Portfolio Recommendation from Clipboard...
--------------------
📋 CLIPBOARD CONTENT:
ACTION,TICKER,QTY,TYPE,LIMIT_PRICE,STOP_LOSS,TAKE_PROFIT,REASON
CANCEL,CLSK,30,N/A,N/A,N/A,N/A,Order stale (>10% away) and switch to Stop Loss Only policy
CANCEL,CORZ,10,N/A,N/A,N/A,N/A,Order stale (>10% away) and switch to Stop Loss Only policy
HOLD,CLSK,30,N/A,N/A,12.35,N/A,Trend > 50SMA; updated stop below 50SMA
HOLD,CORZ,10,N/A,N/A,16.20,N/A,Trend > 50SMA; updated stop below 50SMA
HOLD,RIOT,13,N/A,N/A,16.50,N/A,Trend > 50SMA; maintaining existing stop
HOLD,UPST,4,N/A,N/A,43.95,N/A,Above 50SMA; maintaining existing stop
NO_TRADES,N/A,N/A,N/A,N/A,N/A,N/A,Insufficient buying power ($9.17)
--------------------

🔎 Found 7 trade(s) (CSV).

🚫 PROCESSING CANCEL: CLSK
   🧹 Cancelling 2 active order(s) for CLSK...
   ✅ Cancelled order 85e5f8aa-a8b9-4a64-b4b2-582d0b791764
   ✅ Cancelled order 65119b36-d2ff-4caf-96b5-58ec86c37710
   ✅ All orders for CLSK successfully cancelled.

🚫 PROCESSING CANCEL: CORZ
   🧹 Cancelling 2 active order(s) for CORZ...
   ✅ Cancelled order dedf8868-54c7-4610-ad0c-a91884e03eb9
   ✅ Cancelled order 5474320e-215d-4667-b751-66d709849692
   ✅ All orders for CORZ successfully cancelled.

🛡️ SYNCING PROTECTION: CLSK (Target Stop: $12.35)
   ➕ Missing Protection: No stop-loss found for CLSK.
   ✅ SUCCESS: New stop-loss placed for CLSK @ $12.35

🛡️ SYNCING PROTECTION: CORZ (Target Stop: $16.20)
   ➕ Missing Protection: No stop-loss found for CORZ.
   ✅ SUCCESS: New stop-loss placed for CORZ @ $16.20

🛡️ SYNCING PROTECTION: RIOT (Target Stop: $16.50)
   ✅ Already Protected: Existing stop for RIOT matches $16.50 (new)

🛡️ SYNCING PROTECTION: UPST (Target Stop: $43.95)
   ✅ Already Protected: Existing stop for UPST matches $43.95 (new)
� NO_TRADES: AI explicitly decided to stay flat today (None).
```
