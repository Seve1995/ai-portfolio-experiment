"""
AI Portfolio Experiment V2 — Dashboard Exporter

Reads the granular agent portfolio states and outputs the aggregated 
JSON and CSV formats required by the existing V1 Dashboard.
"""

import json
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def export_for_dashboard(data_dir: Path, output_dir: Path):
    """
    Export all V2 portfolio data to V1 Dashboard formats.
    Reads from: v2/data/portfolios/*_history.json
    Writes to: v1/logs/portfolios.json, v1/logs/transactions.json, v1/logs/performance.csv
    """
    logger.info("Exporting V2 data to Dashboard format...")
    
    portfolios_dir = data_dir / "portfolios"
    if not portfolios_dir.exists():
        logger.warning("No portfolios directory found. Run agents first.")
        return
        
    dashboard_portfolios = {}
    dashboard_transactions = []
    
    csv_rows = ["Date,Agent,Portfolio Value,Cash,Positions"]
    
    # Process history for each agent
    for hist_file in portfolios_dir.glob("*_history.json"):
        agent_id = hist_file.stem.replace("_history", "")
        
        with open(hist_file) as f:
            historian = json.load(f)
            
        if not historian:
            continue
            
        # 1. Portfolios.json format: {"agent_id": {"YYYY-MM-DD": {"cash": ..., "positions": {...}}}}
        # 2. Extract transactions list
        
        agent_portfolios = {}
        for state in historian:
            date_str = state["date"]
            
            # Standardize for dashboard
            dashboard_positions = []
            
            for ticker, pos in state["positions"].items():
                dash_pos = {
                    "symbol": ticker,
                    "qty": pos["shares"],
                    "avg_price": pos["entry_price"],
                    "current_price": pos["current_price"],
                    "market_value": pos["shares"] * pos["current_price"],
                    "unrealized_pl": pos.get("unrealized_pnl", 0.0),
                    "unrealized_pl_pct": pos.get("unrealized_pnl_pct", 0.0) * 100
                }
                dashboard_positions.append(dash_pos)
                
            agent_portfolios[date_str] = {
                "timestamp": date_str,
                "cash": state["cash"],
                "portfolio_value": state["portfolio_value"],
                "positions": dashboard_positions
            }
            
            # CSV Row
            csv_rows.append(f"{date_str},{agent_id},{state['portfolio_value']},{state['cash']},{len(dashboard_positions)}")
            
            # Transactions
            for trade in state.get("transactions_today", []):
                dashboard_transactions.append({
                    "date": date_str,
                    "agent": agent_id,
                    "action": trade["action"],
                    "symbol": trade["ticker"],
                    "qty": trade["shares"],
                    "price": trade["price"],
                    "reasoning": trade.get("reason", "")
                })
                
        dashboard_portfolios[agent_id] = agent_portfolios
        
    # Sort transactions by date descending
    dashboard_transactions.sort(key=lambda x: x["date"], reverse=True)
    
    # Write output files
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "portfolios.json", "w") as f:
        json.dump(dashboard_portfolios, f, indent=2)
        
    with open(output_dir / "transactions.json", "w") as f:
        json.dump(dashboard_transactions, f, indent=2)
        
    with open(output_dir / "performance.csv", "w") as f:
        f.write("\n".join(csv_rows))
        
    # Last updated
    with open(output_dir / "last_updated.json", "w") as f:
        json.dump({"timestamp": datetime.now().isoformat()}, f, indent=2)
        
    logger.info(f"Dashboard export complete. Exported {len(dashboard_portfolios)} agents.")
