"""
AI Portfolio Experiment V2 — Main Entrypoint

Flags:
  --day-0         Run the meta-strategy generation for all agents (setup)
  --run-date      Execute the daily loop for a specific date (YYYY-MM-DD). Defaults to today.
  --export        Export the V2 data to V1 dashboard format.
"""

import argparse
import logging
from datetime import date
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("V2_Main")

def main():
    parser = argparse.ArgumentParser(description="AI Portfolio Experiment V2")
    parser.add_argument("--day-0", action="store_true", help="Generate Day 0 Playbooks")
    parser.add_argument("--run-date", type=str, default=date.today().isoformat(), help="Simulation date YYYY-MM-DD")
    parser.add_argument("--export", action="store_true", help="Export to Dashboard format")
    
    args = parser.parse_args()
    
    # Needs dotenv to load keys
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
    except ImportError:
        logger.warning("python-dotenv not installed. Using system environment variables.")

    if args.day_0:
        logger.info("Running Day 0 Meta Strategy generation...")
        from v2.meta_strategy import generate_playbooks
        generate_playbooks()
        
    # Always run the daily loop unless ONLY export or Day 0 was intended
    # If they specify a run date, we run it. If default, run it.
    if not args.day_0 and not args.export:
        logger.info(f"Running daily loop for {args.run_date}...")
        from v2.agent_runner import run_all_agents
        run_all_agents(args.run_date)
        # Auto-export after a run
        args.export = True
        
    if args.export:
        logger.info("Exporting to Dashboard...")
        from v2.dashboard_exporter import export_for_dashboard
        data_dir = Path(__file__).parent / "data"
        out_dir = Path(__file__).parent.parent / "v1" / "logs"
        export_for_dashboard(data_dir, out_dir)

if __name__ == "__main__":
    main()
