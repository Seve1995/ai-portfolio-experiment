"""
AI Portfolio Experiment V2 — Agent Runner

The main execution engine.
Iterates over all defined agents, injects the daily snapshot and their meta-strategy playbook,
provides the MCP tools, and runs the LLM loop until it proposes trades.
Validates the trades with the PortfolioSimulator and commits them for T+1 execution.
"""

import os
import json
import logging
from pathlib import Path

from .config import AGENTS, RULES, PERSONA_MODIFIERS
from .mcp_servers import get_tool_definitions
from .api_adapters import UnifiedLLMClient
from .portfolio_simulator import PortfolioSimulator

logger = logging.getLogger(__name__)

# Force propose_trades as a tool that MUST be called to end the turn.
def get_trade_tool() -> dict:
    # Load schema
    schema_path = Path(__file__).parent / "schemas" / "propose_trades.json"
    with open(schema_path) as f:
        schema = json.load(f)
        
    return {
        "name": "propose_trades",
        "description": "Submit your final daily trading decisions. You MUST call this tool when you are done analyzing.",
        "parameters": schema
    }

def build_system_prompt(agent_config, playbook: str) -> str:
    """Build the robust system prompt combining rules, persona, and the Day 0 playbook."""
    prompt = f"YOU ARE {agent_config.display_name}.\n\n"
    
    prompt += "=== SYSTEM RULES ===\n"
    for rule_name, rule_val in RULES.__dict__.items():
        prompt += f"- {rule_name}: {rule_val}\n"
        
    prompt += "\n=== YOUR PERSONA ===\n"
    prompt += f"{PERSONA_MODIFIERS[agent_config.persona]}\n"
        
    prompt += "\n=== YOUR INVESTMENT PLAYBOOK (META-STRATEGY) ===\n"
    prompt += "You defined this strategy on Day 0. You MUST adhere to it.\n"
    prompt += f"{playbook}\n\n"
    
    prompt += "=== INSTRUCTIONS ===\n"
    prompt += "1. Analyze the daily snapshot and use tools to investigate further if needed.\n"
    prompt += "2. Determine if you want to buy, sell, or hold.\n"
    prompt += "3. You MUST end your turn by calling the `propose_trades` tool.\n"
    
    return prompt

def build_user_prompt(snapshot: dict, portfolio_state: dict) -> str:
    prompt = f"Market Date: {snapshot['date']}\n\n"
    
    prompt += "=== DAILY SNAPSHOT ===\n"
    prompt += f"{snapshot['market_summary']}\n\n"
    
    prompt += "=== YOUR PORTFOLIO STATE ===\n"
    prompt += json.dumps(portfolio_state, indent=2) + "\n\n"
    
    prompt += "What are your trading decisions for tomorrow (T+1)? Use your tools, then call propose_trades."
    return prompt


def run_agent(agent_id: str, snapshot: dict, simulator: PortfolioSimulator):
    """Run a single agent for the current day."""
    from .config import AGENTS
    
    if agent_id not in AGENTS:
        logger.error(f"Agent {agent_id} not found in config.")
        return
        
    agent = AGENTS[agent_id]
    
    # 1. Simulator pre-LLM checks (T+1 execution of yesterday's trades, check stops)
    # Getting today's OHLC and opening prices.
    # We cheat a bit using the daily snapshot or fetch OHLC locally. 
    # For now, we fetch OHLC for all tickers in portfolio or pending orders
    tickers_needed = set(simulator.position_tickers + [o.ticker for o in simulator.pending_orders])
    
    # Needs to fetch actual prices for today
    from .daily_snapshot import fetch_ohlc_for_tickers
    ohlc_data = fetch_ohlc_for_tickers(list(tickers_needed)) if tickers_needed else {}
    
    # Assuming open_prices are same as ohlc "open" and close_prices are "close"
    open_prices = {t: data["open"] for t, data in ohlc_data.items() if "open" in data}
    close_prices = {t: data["close"] for t, data in ohlc_data.items() if "close" in data}

    # Execute simulator's daily tasks BEFORE LLM (so LLM sees accurate EOD portfolio)
    simulator.check_stops_and_targets(ohlc_data, snapshot["date"])
    simulator.execute_pending_orders(open_prices, snapshot["date"])
    simulator.mark_to_market(close_prices, snapshot["date"])

    # Random agent bypasses LLM logic entirely
    if agent.id == "random_control":
        from .random_agent import execute_random_trades
        result_json = json.dumps(execute_random_trades(simulator.get_portfolio_summary()))
    else:
        # Load agent's Day 0 playbook
        from .config import PLAYBOOKS_DIR
        playbook_path = PLAYBOOKS_DIR / f"{agent_id}.md"
        if not playbook_path.exists():
            playbook = "Default strategy: Maximize risk-adjusted returns."
        else:
            with open(playbook_path) as f:
                playbook = f.read()

        # Get tools
        tools = get_tool_definitions()
        tools.append(get_trade_tool())

        # Build prompts
        sys_prompt = build_system_prompt(agent, playbook)
        user_prompt = build_user_prompt(snapshot, simulator.get_portfolio_summary())

        logger.info(f"Starting LLM execution for {agent_id} ({agent.provider.name})...")
        
        client = UnifiedLLMClient(agent.provider)
        try:
            result_json = client.generate(sys_prompt, user_prompt, tools, max_tool_calls=12)
        except Exception as e:
            logger.error(f"Agent {agent_id} crashed: {e}")
            result_json = ""

    # Process LLM output
    if result_json:
        try:
            trades_data = json.loads(result_json)
            trades = trades_data.get("trades", [])
            logger.info(f"{agent_id} proposed: {len(trades)} trades.")
            
            # Submit to simulator
            simulator.submit_orders(trades, snapshot["date"])
            
        except json.JSONDecodeError:
            logger.error(f"{agent_id} returned invalid JSON: {result_json}")
    else:
        logger.error(f"{agent_id} failed to propose trades.")
        
    # Save simulator state for this day
    simulator.save_state()
    simulator.save_snapshot_history()


def run_all_agents(snapshot_date: str):
    """Main entry point for running all agents on a specific date."""
    from .daily_snapshot import build_daily_snapshot
    from datetime import date
    from .config import AGENTS, STARTING_CAPITAL, RULES, PORTFOLIOS_DIR, SNAPSHOTS_DIR
    
    logger.info(f"--- STARTING DAILY RUN: {snapshot_date} ---")
    
    dt = date.fromisoformat(snapshot_date)
    snapshot = build_daily_snapshot(dt, save_dir=SNAPSHOTS_DIR)
    
    if not snapshot.get("is_market_day", True):
        logger.info(f"{snapshot_date} is not a market day. Skipping.")
        return
        
    # Run agents
    for agent_id in AGENTS.keys():
        simulator = PortfolioSimulator(agent_id, STARTING_CAPITAL, RULES, PORTFOLIOS_DIR)
        run_agent(agent_id, snapshot, simulator)

    logger.info("--- DAILY RUN COMPLETE ---")
