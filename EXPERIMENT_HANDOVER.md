# 🦾 AI Portfolio Experiment V2: Institutional Handover Dossier

> **DATE**: 2026-04-11  
> **STATUS**: PROPER DAY 1 READY (CLEAN SLATE)  
> **CONTEXT**: 18-Agent Autonomous Roster with Market Intelligence Hub (MIH).

## 1. The Core Objective
Benchmarking 18 autonomous agents (6 models × 3 personas) across a 6-month simulation in the 2026 high-rate, AI-volatile regime. Every agent starts with exactly **$10,000** on Day 1.

## 2. Technical Architecture (V2 "Institutional")
We transitioned from the reactive V1 "Deep Search" to a deterministic MIH model.

### 🧠 Market Intelligence Hub (MIH)
- **Data Load**: 150KB hyper-dense payload (TOON Markdown Tables).
- **Macro Indicators**: Driven by FRED (Yields, VIX, Spreads).
- **RRG Rotation Math**: Uses a 90-day window to map institutional capital flows.
- **Dynamic Discovery (CRITICAL)**: To avoid human bias, the engine identifies the Top 3 "Strength" sectors (Leading/Improving) and automatically injects their Top 10 holdings into the candidate pool for catalyst scanning.

### 🛡️ "Code is Law" Simulator
- **Constraints**: T+1 fills at Open, Max 25% sizing, mandatory ATR-based Stop-Losses.
- **Precision**: The runner now fetches actual `High/Low` bars for the day to ensure real-world fidelity for stop-loss execution.

## 3. Recent Structural Stabilizations
The following fixes were applied to transition from "test" to "proper" execution:
- **Roster Jitter**: Implemented a randomized 5-15 second delay between agents in `v2/agent_runner.py` to prevent `429 Rate Limit` crashes during the 18-agent roster run.
- **Unbiased Logic**: Rewrote `v2/snapshot_engine.py` to remove hardcoded sector lists in favor of purely RRG-driven discovery.
- **Automation Pipeline**: Configured `.github/workflows/daily_simulation.yml` to run the "Forever Loop" daily at 21:00 UTC with automated persistence via `git-auto-commit`.

## 4. Current State & Launch Sequence
The environment is currently in a **CLEAN SLATE** state. All test portfolios and snapshots have been purged.

### ⚡ NEXT STEPS (FOR THE NEXT AI INSTANCE):
1. **GitHub Secrets**: Ensure the user has added `BRAVE_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, and `FRED_API_KEY` to the repo secrets.
2. **Trigger Proper Day 1**: Manually trigger the "Daily Portfolio Simulation" via the GitHub Actions tab.
3. **Verify Alpha**: Audit the first official MIH snapshot to ensure the "Dynamic Discovery" is correctly picking up leaders in the 2026 regime (e.g., Energy/Defense during the Iran conflict).

## 📁 Key File Inventory
- `v2/snapshot_engine.py`: Data ingestion, RRG, and Dynamic Alpha logic.
- `v2/agent_runner.py`: Orchestrator of the 18 agents (includes Jitter).
- `v2/portfolio_simulator.py`: Trade validation, execution, and PnL math.
- `.github/workflows/daily_simulation.yml`: The "Forever Loop" configuration.
- `v2/data/`: Current home for snapshots, portfolios (initially $10k), and logs.

---
*End of Handover.*
