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

from .config import AGENTS, SYSTEM_RULES
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
    prompt = f"YOU ARE {agent_config.name}.\n\n"
    
    prompt += "=== SYSTEM RULES ===\n"
    for rule in SYSTEM_RULES:
        prompt += f"- {rule}\n"
        
    prompt += "\n=== YOUR PERSONA ===\n"
    prompt += f"{agent_config.persona.description}\n"
    prompt += "Traits: " + ", ".join(agent_config.persona.traits) + "\n"
    if agent_config.persona.bias:
        prompt += f"Bias: {agent_config.persona.bias}\n"
        
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
    if agent_id not in AGENTS:
        logger.error(f"Agent {agent_id} not found in config.")
        return
        
    agent = AGENTS[agent_id]
    
    # Random agent bypasses LLM logic entirely
    if agent.provider.name == "Random Control":
        from .random_agent import execute_random_trades
        trades = execute_random_trades(simulator.get_agent_state(agent_id))
        simulator.submit_trades(agent_id, trades, snapshot["date"])
        logger.info(f"{agent_id} (Random Control) executed.")
        return

    # Load agent's Day 0 playbook
    playbook_path = Path(__file__).parent / "data" / "playbooks" / f"{agent_id}.md"
    if not playbook_path.exists():
        logger.warning(f"No playbook found for {agent_id}. Using default.")
        playbook = "Default strategy: Maximize risk-adjusted returns."
    else:
        with open(playbook_path) as f:
            playbook = f.read()

    # Get tools
    tools = get_tool_definitions()
    tools.append(get_trade_tool())

    # Build prompts
    sys_prompt = build_system_prompt(agent, playbook)
    user_prompt = build_user_prompt(snapshot, simulator.get_agent_state(agent_id))

    logger.info(f"Starting execution for {agent_id} ({agent.provider.name})...")
    
    client = UnifiedLLMClient(agent.provider)
    try:
        result_json = client.generate(sys_prompt, user_prompt, tools, max_tool_calls=12)
        
        if result_json:
            try:
                trades = json.loads(result_json)
                logger.info(f"{agent_id} proposed: {len(trades.get('trades', []))} trades.")
                
                # Submit to simulator (firewall block)
                # Note: simulator handles validation, bounds, sizing enforcement
                simulator.submit_trades(agent_id, trades, snapshot["date"])
                
            except json.JSONDecodeError:
                logger.error(f"{agent_id} returned invalid JSON: {result_json}")
                simulator.submit_trades(agent_id, {"reasoning": "Failed to output valid JSON", "trades": []}, snapshot["date"])
        else:
            logger.error(f"{agent_id} failed to propose trades.")
            simulator.submit_trades(agent_id, {"reasoning": "Failed to call propose_trades", "trades": []}, snapshot["date"])
            
    except Exception as e:
        logger.error(f"Agent {agent_id} crashed: {e}")
        simulator.submit_trades(agent_id, {"reasoning": f"Crash: {e}", "trades": []}, snapshot["date"])


def run_all_agents(snapshot_date: str):
    """Main entry point for running all agents on a specific date."""
    from .daily_snapshot import build_daily_snapshot
    from datetime import date
    
    logger.info(f"--- STARTING DAILY RUN: {snapshot_date} ---")
    
    dt = date.fromisoformat(snapshot_date)
    snapshot = build_daily_snapshot(dt, save_dir=Path(__file__).parent / "data" / "snapshots")
    
    if not snapshot["is_market_day"]:
        logger.info(f"{snapshot_date} is not a market day. Skipping.")
        return
        
    simulator = PortfolioSimulator()
    
    # Determine the execution date for trades submitted yesterday
    # In live mode simulation, we would fetch today's actual open prices
    # We will let simulator resolve prices dynamically
    simulator.process_pending_trades(snapshot_date, snapshot)

    # Run agents to propose trades for tomorrow
    for agent_id in AGENTS.keys():
        run_agent(agent_id, snapshot, simulator)

    logger.info("--- DAILY RUN COMPLETE ---")
