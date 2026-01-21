# AI Portfolio Experiment: LLM Comparative Trading Study

A Python-based framework for benchmarking Large Language Models (LLMs) in algorithmic trading. This project imposes a strict, rules-based environment to evaluate the financial decision-making capabilities of **ChatGPT (5.2)**, **Gemini (3 Pro)**, **Claude (4.5 Opus)**, and **Perplexity (Pro)**.

## Overview

This experiment eliminates prompting variability to isolate model performance. Each model acts as an autonomous Portfolio Manager starting with $1,000, operating under identical constraints.

**Architecture:**
1.  **Data Pipeline**: Fetches real-time portfolio state (Alpaca API) and market data (Yahoo Finance).
2.  **Prompt Engineering**: Generates a deterministic, context-rich prompt containing standardized macro/technical indicators.
3.  **Execution Engine**: Parses structured model outputs (Markdown/CSV) and routes orders to Alpaca Paper Trading.

## Project Structure

- `config.py`: Centralized configuration, paths, and model selection logic.
- `scripts/`:
  - `generate_prompt.py`: Fetches account and macro data, then generates and copies a PM-style prompt to your clipboard.
  - `execute_trade.py`: Parses AI output from the clipboard (Markdown tables or CSV) and executes trades on Alpaca with safety checks.
  - `check_history.py`: Displays recent account activity, including fills and order status.
  - `log_performance.py`: Rebuilds performance history from Alpaca and saves to `logs/performance.csv`.
  - `generate_substack_report.py`: Generates a Markdown report for Substack based on performance data.
- `index.html`: Interactive performance dashboard (located in the root for GitHub Pages).
- `requirements.txt`: List of Python dependencies.
- `.env`: (User-created) Stores sensitive API keys.

## Setup

1. **Clone the repository.**
2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables**:
   Create a `.env` file in the root directory with your Alpaca Paper Trading keys:
   ```text
   ALPACA_KEY=your_api_key_here
   ALPACA_SECRET=your_api_secret_here
   ```

## Usage

### 1. Generate Prompt
Run the generator to gather data and prepare the AI prompt:
```bash
python scripts/generate_prompt.py
```
*The prompt is automatically copied to your clipboard. Paste it into your preferred AI.*

### 2. Execute Trades
After the AI provides an execution table, copy that table to your clipboard and run:
```bash
python scripts/execute_trade.py
```
To preview trades without executing, use the dry-run flag:
```bash
python scripts/execute_trade.py --dry-run
```

### 3. Check Status
View your recent trade history and fills:
```bash
python scripts/check_history.py
```

## Safety Features

- **Idempotency**: `execute_trade.py` checks for existing positions and open orders to prevent duplicate trades.
- **Buying Power**: Validates that enough buying power exists before attempting a purchase.
- **Stop-Loss Validation**: Ensures stop-loss levels are logical relative to entry prices.
- **Position Protection**: Automatically manages stop-loss orders for current holdings.

## License

MIT
