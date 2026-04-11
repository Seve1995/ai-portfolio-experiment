
import logging
import json
from pathlib import Path
from datetime import date
from v2.agent_runner import run_agent
from v2.portfolio_simulator import PortfolioSimulator
from v2.daily_snapshot import load_snapshot
from v2.config import AGENTS, STARTING_CAPITAL, RULES, PORTFOLIOS_DIR, SNAPSHOTS_DIR

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s - %(message)s')
logger = logging.getLogger("SmokeTest_Phase2")

def main():
    run_date = date(2026, 4, 7)
    snapshot = load_snapshot(run_date, SNAPSHOTS_DIR)
    
    if not snapshot:
        logger.error(f"No snapshot found for {run_date}. Run build_daily_snapshot first.")
        return

    # Phase 2: All remaining 12 agents (Conservative & Aggressive)
    balanced_ids = [
        "chatgpt_balanced", "claude_balanced", "gemini_balanced",
        "mistral_balanced", "deepseek_balanced", "qwen_balanced"
    ]
    
    target_agents = [aid for aid in AGENTS.keys() if aid not in balanced_ids and aid != "random_control"]

    logger.info(f"--- STARTING SMOKE TEST PHASE 2: {len(target_agents)} AGENTS ---")

    for agent_id in target_agents:
        logger.info(f"Running agent: {agent_id}")
        simulator = PortfolioSimulator(agent_id, STARTING_CAPITAL, RULES, PORTFOLIOS_DIR)
        
        try:
            run_agent(agent_id, snapshot, simulator)
            logger.info(f"Finished agent: {agent_id}")
        except Exception as e:
            logger.error(f"Error running agent {agent_id}: {e}")

    logger.info("--- PHASE 2 COMPLETE ---")

if __name__ == "__main__":
    main()
