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
    positions = portfolio_state["positions"]
    
    trades = []
    
    # 1. Randomly decide to sell existing positions (20% chance per day per position)
    for ticker, pos in positions.items():
        if random.random() < 0.20:
            qty_to_sell = pos["qty"]  # Simplification: sell all
            trades.append({
                "action": "SELL",
                "ticker": ticker,
                "quantity_pct": 1.0,
                "reasoning": "Random coin flip decided to sell."
            })
            
    # 2. Randomly decide to buy new positions IF we have cash and slot space
    # Max slots = 15
    open_slots = 15 - len(positions) + len(trades) # rough estimate including the sells
    
    if cash > 1000 and open_slots > 0:
        # Number of new trades (1 to 3, bounded by slots)
        num_buys = min(random.randint(1, 3), open_slots)
        
        candidates = [t for t in UNIVERSE if t not in positions]
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
                
            qty_pct = target_amount / cash
            cash -= target_amount
            
            # Random stop loss between 3% and 15%
            stop_loss = round(random.uniform(3.0, 15.0), 1)
            
            # Random take profit between 10% and 50% (or None half the time)
            take_profit = round(random.uniform(10.0, 50.0), 1) if random.random() > 0.5 else None
            
            trades.append({
                "action": "BUY",
                "ticker": ticker,
                "cash_pct": round(qty_pct, 2),
                "stop_loss_pct": stop_loss,
                "take_profit_pct": take_profit,
                "reasoning": "Randomly selected from liquid universe."
            })

    logger.info(f"Random Agent generated {len(trades)} trades.")
    return {
        "reasoning": "I am the random control agent. I flipped coins.",
        "trades": trades
    }
