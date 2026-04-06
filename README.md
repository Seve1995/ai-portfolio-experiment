# AI Portfolio Experiment (V2): Automated Agentic LLM Study

A Python-based, fully automated framework for benchmarking Large Language Models (LLMs) in algorithmic trading. This project imposes a strict, rules-based environment to evaluate the financial decision-making capabilities of 18 AI agents (6 models × 3 personas) and 1 Random Control baseline.

**Models Tested**: ChatGPT (OpenAI), Claude (Anthropic), Gemini (Google), Mistral, DeepSeek, and Qwen.

## Overview

Unlike V1 (which required manual execution via Alpaca and clipboard manipulation), **V2 is completely autonomous and agentic**. 
Each agent acts as a virtual Portfolio Manager starting with $10,000 in a deterministic paper-trading simulator ("Code is Law"). 

**Architecture Pipeline:**
1. **Daily Snapshot**: Fetches identical daily market OHLC, macro indicators (FRED), and news (Finnhub) for all agents to enforce *fairness*.
2. **LLM Orchestration**: Injects the snapshot and a Day-0 custom "Playbook" into each agent's context, giving them access to MCP Server tools (Search, Fundamentals, Technicals). 
3. **Portfolio Simulator**: Validates structured trades against system limits (max 25% sizing, mandatory stop-losses, no shorts) and executes them deterministically at T+1 open prices with slippage.
4. **Dashboard Exporter**: Dumps aggregated JSON and CSV data, directly powering the GitHub Pages Dashboard.

## Project Structure

- `v2/config.py`: Core system rules, agent personas, and API provider definitions.
- `v2/agent_runner.py`: Orchestrator driving the daily LLM inference loop and Tool execution.
- `v2/portfolio_simulator.py`: Strict validation firewall and T+1 execution engine.
- `v2/daily_snapshot.py`: Scrapes market ground-truth (YFinance, FRED, News).
- `v2/mcp_servers/`: Custom tools for LLMs (Sanitized Web Search, Technicals, Fundamentals).
- `v2/dashboard_exporter.py`: Outputs simulator state to `v1/logs/` formats for the UI.
- `index.html`: The static React Dashboard (serves data from `v1/logs/`).

## Setup

1. **Clone and create a virtual environment**:
   ```bash
   git clone <repo_url>
   cd ai-portfolio-experiment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
2. **Install V2 Dependencies**:
   ```bash
   pip install -r v2/requirements.txt
   ```
3. **Configure Environment Variables**:
   Copy the example environment file and fill in your API keys (you don't strictly need all of them to test single models):
   ```bash
   cp .env.example .env
   ```

## Usage

### 1. Generate Strategy Playbooks (Day 0)
Run exactly once to have each LLM write its own distinct trading constitution, ensuring consistency over the 6-month simulation:
```bash
python -m v2.main --day-0
```

### 2. Run the Daily Execution Loop
Execute the core orchestrator for a specific market day. This updates prices, checks stop-losses, requests LLM trade proposals, and marks portfolios to market:
```bash
python -m v2.main --run-date 2026-07-06
```

*(Note: Data extraction formats automatically sync to the existing web dashboard!)*

## Safety Rules & "Code is Law"

LLMs are prone to hallucination. Therefore, the Portfolio Simulator strictly enforces:
- **No Penny Stocks / Shorts / Crypto**: Filtered out cleanly.
- **Sizing Boundaries**: 5% minimum to 25% maximum portfolio weight per position.
- **Mandatory Stop-Loss**: Trades proposed without stop-loss levels are forcefully rejected.
- **Fair Ground-Truth**: Agents only know what the Daily Snapshot specifies.

## License
MIT
