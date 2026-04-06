"""
AI Portfolio Experiment V2 — Meta Strategy (Day 0)

This script is run exactly ONCE per agent at the start of the experiment (Day 0).
It asks the LLM to define its custom trading strategy (universe, horizon, risk tolerance, indicators).
The resulting "Playbook" is saved to disk and injected into the prompt *every single day*
to prevent the LLM from drifting from its initial strategy.
"""

import os
import logging
from pathlib import Path

from .config import AGENTS, SYSTEM_RULES
from .api_adapters import UnifiedLLMClient

logger = logging.getLogger(__name__)

DAY_0_PROMPT = """
You are about to begin a 6-month autonomous trading experiment. 
You will be competing against other LLMs and a benchmark index.
Before we start, you must define your "Meta-Strategy" (Investment Playbook).

This playbook will be injected into your prompt every single day for the next 6 months. 
You must adhere to it.

=== SYSTEM CONSTRAINTS ===
- Capital: $10,000
- Execution: T+1 Next Open (No day trading possible)
- Instrument Universe: US Equities (price >= $5) and ETFs. NO penny stocks, NO crypto, NO options.
- Position Sizing: 5% to 25% per trade. Max 15 open positions.
- Risk Management: The system enforces a mandatory Stop-Loss. But YOU must decide where to place it.

Please define your Playbook answering the following:
1. Core Strategy: Are you value, growth, momentum, mean-reversion, or macro-driven?
2. Asset Selection: How will you pick stocks? What sectors will you favor? Will you use ETFs?
3. Trade Horizon: How long do you expect to hold a typical position?
4. Risk Profile: What will be your typical Stop-Loss % and Take-Profit %?
5. Data Usage: Which of your available tools (FRED macro, FINRA news, Technicals, Fundamentals) will you prioritize?

Output a detailed, structured markdown document. This is your constitution.
No greetings, just the markdown document.
"""

def generate_playbooks():
    """Run Day 0 prompt for all agents."""
    playbooks_dir = Path(__file__).parent / "data" / "playbooks"
    playbooks_dir.mkdir(parents=True, exist_ok=True)
    
    for agent_id, config in AGENTS.items():
        if config.provider.name == "Random Control":
            continue
            
        playbook_path = playbooks_dir / f"{agent_id}.md"
        if playbook_path.exists():
            logger.info(f"Playbook already exists for {agent_id}. Skipping.")
            continue
            
        logger.info(f"Generating Day 0 Playbook for {agent_id}...")
        
        system_prompt = f"YOU ARE {config.name}.\nPersona: {config.persona.description}\nBias: {config.persona.bias}\n"
        
        client = UnifiedLLMClient(config.provider)
        try:
            # We don't provide tools for the Day 0 prompt, just ask for the strategy text
            playbook = client.generate(system_prompt, DAY_0_PROMPT, tools=[], max_tool_calls=0)
            
            with open(playbook_path, "w") as f:
                f.write(playbook)
                
            logger.info(f"Playbook saved for {agent_id}.")
        except Exception as e:
            logger.error(f"Failed to generate playbook for {agent_id}: {e}")

if __name__ == "__main__":
    generate_playbooks()
