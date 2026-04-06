"""
AI Portfolio Experiment V2 — Random Control Agent

This agent makes completely random trades within the system constraints.
Serves as the ultimate baseline: if an LLM cannot beat this agent, 
its "intelligence" has zero or negative alpha.
"""

import random
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# A predefined universe of standard liquid stocks/ETFs for the random agent
UNIVERSE = [
    "SPY", "QQQ", "IWM", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", 
    "META", "TSLA", "BRK.B", "UNH", "JNJ", "XOM", "JPM", "V", "PG", 
    "MA", "COST", "HD", "ABBV", "MRK", "CVX", "PEP", "KO", "BAC", 
    "PFE", "TMO", "CSCO", "MCD", "DIS", "WMT", "AMD", "NFLX"
]

def execute_random_trades(portfolio_state: Dict) -> Dict:
    """
    Generate random trades adhering to system constraints.
    - Max 15 positions
    - Tries to stay mostly invested over time
    - Random stop losses
    """
    cash = portfolio_state["cash"]
    positions = portfolio_state["positions"]  # This is a list of dicts
    
    trades = []
    
    # 1. Randomly decide to sell existing positions (20% chance per day per position)
    for pos in positions:
        ticker = pos["ticker"]
        if random.random() < 0.20:
            trades.append({
                "action": "SELL",
                "ticker": ticker,
                "allocation_pct": 100,  # Sell 100% of the position
                "order_type": "MARKET",
                "stop_loss_pct": 10, # Doesn't matter for sell
                "reason": "Random control sell decision."
            })
            
    # 2. Randomly decide to buy new positions IF we have cash and slot space
    # Max slots = 15
    open_slots = 15 - len(positions) + len(trades) # rough estimate including the sells
    
    if cash > 1000 and open_slots > 0:
        # Number of new trades (1 to 3, bounded by slots)
        num_buys = min(random.randint(1, 3), open_slots)
        
        # Get list of existing tickers string
        existing_tickers = [p["ticker"] for p in positions]
        
        candidates = [t for t in UNIVERSE if t not in existing_tickers]
        random.shuffle(candidates)
        
        for i in range(num_buys):
            if not candidates:
                break
            ticker = candidates.pop()
            
            # Random sizing between 5% and 15% of TOTAL initial capital (10000), 
            # but constrained by current cash
            target_amount = random.uniform(500, 1500)
            if target_amount > cash:
                target_amount = cash
                
            qty_pct = (target_amount / portfolio_state["portfolio_value"]) * 100
            
            # Clamp between 5 and 25
            qty_pct = max(5.0, min(qty_pct, 25.0))
            
            cash -= target_amount
            
            # Random stop loss between 3% and 15%
            stop_loss = round(random.uniform(3.0, 15.0), 1)
            
            # Random take profit between 10% and 50% (or None half the time)
            take_profit = round(random.uniform(10.0, 50.0), 1) if random.random() > 0.5 else None
            
            trade = {
                "action": "BUY",
                "ticker": ticker,
                "allocation_pct": round(qty_pct, 2),
                "order_type": "MARKET",
                "stop_loss_pct": stop_loss,
                "reason": "Randomly selected from liquid universe."
            }
            if take_profit:
                trade["take_profit_pct"] = take_profit
                
            trades.append(trade)

    logger.info(f"Random Agent generated {len(trades)} trades.")
    
    # Needs to match schema!
    return {
        "daily_notes": "I am a monkey throwing darts at a board.",
        "trades": trades,
        "portfolio_review": []
    }
