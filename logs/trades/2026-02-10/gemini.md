# Trade Execution Log

**Model:** Gemini
**Date:** 2026-02-10

```text

==================================================
📊 ALPACA PRE-FLIGHT STATUS (Gemini)
==================================================
💰 Equity: $954.77
💸 Buying Power: $523.29

📂 Current Positions:
   • GME: 12 shares @ $24.88 (Current: $24.56)
   • SMCI: 4 shares @ $33.34 (Current: $34.19)

📝 Open Orders:
   • GME: LIMIT SELL 12 shares @ $27.48 (new)
   • SMCI: LIMIT SELL 4 shares @ $40.20 (new)
   • SMCI: STOP SELL 4 shares Stop @ $31.50 (OCO-held)
   • GME: STOP SELL 12 shares Stop @ $24.00 (OCO-held)

==================================================

📋 Parsing Portfolio Recommendation from Clipboard...
--------------------
📋 CLIPBOARD CONTENT:
ACTION,TICKER,QTY,TYPE,LIMIT_PRICE,STOP_LOSS,TAKE_PROFIT,REASON
CANCEL,SMCI,4,N/A,N/A,N/A,N/A,Order stale >10% from current price
CANCEL,GME,12,N/A,N/A,N/A,N/A,Order stale; realigning for accumulation
HOLD,SMCI,4,N/A,N/A,31.25,N/A,Trend >50SMA; Fundamental growth confirmed
HOLD,GME,12,N/A,N/A,22.10,N/A,Insider buying; Trend >20&50SMA
BUY,GME,5,LIMIT,24.65,22.10,29.75,Valid Setup: SI>15%; Trend Up; Mar Catalyst
--------------------

🔎 Found 5 trade(s) (CSV).

🚫 PROCESSING CANCEL: SMCI
   🧹 Cancelling 2 active order(s) for SMCI...
   ✅ Cancelled order 24d03668-9472-4462-9fe0-97e0d0cdf48f
   ✅ Cancelled order 952a8173-808a-4328-b5d8-63a775a17ac0
   ✅ All orders for SMCI successfully cancelled.

🚫 PROCESSING CANCEL: GME
   🧹 Cancelling 2 active order(s) for GME...
   ✅ Cancelled order aad939bf-1ec3-41ad-b852-4393d58fa4a1
   ✅ Cancelled order 457c2bbb-bdfb-4942-9bbf-60246dfe3777
   ✅ All orders for GME successfully cancelled.

🛡️ SYNCING PROTECTION: SMCI (Target Stop: $31.25)
   ➕ Missing Protection: No stop-loss found for SMCI.
   ✅ SUCCESS: New stop-loss placed for SMCI @ $31.25

🛡️ SYNCING PROTECTION: GME (Target Stop: $22.10)
   ➕ Missing Protection: No stop-loss found for GME.
   ✅ SUCCESS: New stop-loss placed for GME @ $22.10

🚀 PROCESSING BUY: GME
   ⚠️ Already Owned: You currently hold 12 shares of GME. Skipping execution.
```
