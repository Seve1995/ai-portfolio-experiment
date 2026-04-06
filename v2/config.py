"""
AI Portfolio Experiment V2 — Configuration
All agent definitions, system rules, API settings, and persona modifiers.
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ─────────────────────────────────────────────
# Experiment Parameters
# ─────────────────────────────────────────────

EXPERIMENT_NAME = "AI Portfolio Experiment V2"
EXPERIMENT_START = "2026-07-01"
EXPERIMENT_END = "2026-12-31"
STARTING_CAPITAL = 10_000.00
CURRENCY = "USD"

# ─────────────────────────────────────────────
# System-Enforced Rules ("Code is Law")
# These CANNOT be overridden by any model.
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class SystemRules:
    """Immutable trading rules enforced by the portfolio simulator."""
    min_stock_price: float = 5.00          # Minimum stock price (excludes penny stocks)
    max_position_pct: float = 0.25         # Max 25% of portfolio in one position
    min_position_pct: float = 0.05         # Min 5% of portfolio per trade
    max_positions: int = 15                # Max simultaneous positions
    max_daily_buys: int = 3                # Max new buy orders per day
    slippage_pct: float = 0.001            # 0.1% slippage on all fills
    fractional_shares: bool = True         # Allow fractional share trading
    long_only: bool = True                 # No short selling
    stop_loss_required: bool = True        # Every position must have a stop-loss
    execution_model: str = "T+1_OPEN"      # Decide after close, execute at next open
    stop_trigger_model: str = "OHLC"       # Check High/Low for stop/TP triggers

RULES = SystemRules()

# ─────────────────────────────────────────────
# Personas
# ─────────────────────────────────────────────

class Persona(Enum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"

PERSONA_MODIFIERS = {
    Persona.CONSERVATIVE: (
        "You are a CONSERVATIVE portfolio manager. "
        "Prioritize capital preservation above all else. Prefer established, large-cap companies "
        "and broad-market ETFs. Use smaller position sizes (closer to 5-10%). "
        "Set wider stop-losses to avoid being stopped out by normal volatility. "
        "Target a Sortino ratio above 1.0. Accept lower returns for lower drawdowns."
    ),
    Persona.BALANCED: (
        "You are a BALANCED portfolio manager. "
        "Seek a healthy balance between risk and reward. Mix growth and value opportunities. "
        "Use moderate position sizes (10-15%). Diversify across sectors. "
        "Target consistent returns with controlled drawdowns under 15%."
    ),
    Persona.AGGRESSIVE: (
        "You are an AGGRESSIVE portfolio manager. "
        "Maximize returns. Accept higher drawdowns in pursuit of alpha. "
        "Concentrate on your highest-conviction ideas with larger position sizes (15-25%). "
        "Take advantage of momentum and catalysts. Tighter stop-losses to cut losses fast. "
        "Target the highest Information Ratio against your chosen benchmark."
    ),
}

# ─────────────────────────────────────────────
# LLM Provider Configurations
# ─────────────────────────────────────────────

@dataclass
class LLMProvider:
    """Configuration for a single LLM API provider."""
    name: str
    model_id: str
    api_type: str                          # "openai", "anthropic", "google", "mistral", "deepseek", "qwen", "perplexity"
    api_key_env: str                       # Environment variable name for API key
    base_url: Optional[str] = None         # Custom base URL (for DeepSeek, Qwen, etc.)
    temperature: float = 0.0              # Deterministic output
    max_tokens: int = 4096
    supports_tool_calling: bool = True
    parallel_tool_calls: bool = False      # DISABLED for fairness (even if provider supports it)

PROVIDERS = {
    "chatgpt": LLMProvider(
        name="ChatGPT",
        model_id="gpt-4.1-2026-04-14",
        api_type="openai",
        api_key_env="OPENAI_API_KEY",
    ),
    "gemini": LLMProvider(
        name="Gemini",
        model_id="gemini-3.1-pro",
        api_type="google",
        api_key_env="GOOGLE_API_KEY",
    ),
    "claude": LLMProvider(
        name="Claude",
        model_id="claude-4.6-sonnet",
        api_type="anthropic",
        api_key_env="ANTHROPIC_API_KEY",
    ),

    "mistral": LLMProvider(
        name="Mistral",
        model_id="mistral-large-latest",
        api_type="mistral",
        api_key_env="MISTRAL_API_KEY",
    ),
    "deepseek": LLMProvider(
        name="DeepSeek",
        model_id="deepseek-chat",
        api_type="openai",  # DeepSeek uses OpenAI-compatible format
        api_key_env="DEEPSEEK_API_KEY",
        base_url="https://api.deepseek.com",
    ),
    "qwen": LLMProvider(
        name="Qwen",
        model_id="qwen-max",
        api_type="openai",  # Qwen supports OpenAI-compatible format
        api_key_env="QWEN_API_KEY",
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    ),
}

# ─────────────────────────────────────────────
# Agent Definitions
# ─────────────────────────────────────────────

@dataclass
class Agent:
    """A single trading agent (model + persona combination)."""
    id: str                                # e.g., "chatgpt_conservative"
    display_name: str                      # e.g., "ChatGPT (Conservative)"
    provider_key: str                      # Key into PROVIDERS dict
    persona: Persona
    benchmark: str = "SPY"                 # Default benchmark, updated after Day 0

    @property
    def provider(self) -> LLMProvider:
        return PROVIDERS[self.provider_key]

def _build_agents() -> list[Agent]:
    """Generate all 21 AI agents (7 models × 3 personas) + 1 random control."""
    agents = []
    for provider_key, provider in PROVIDERS.items():
        for persona in Persona:
            agent_id = f"{provider_key}_{persona.value}"
            display_name = f"{provider.name} ({persona.value.title()})"
            agents.append(Agent(
                id=agent_id,
                display_name=display_name,
                provider_key=provider_key,
                persona=persona,
            ))
    # Random control agent
    agents.append(Agent(
        id="random_control",
        display_name="Random Control",
        provider_key="",  # No LLM provider
        persona=Persona.BALANCED,
        benchmark="SPY",
    ))
    return agents
AGENTS = {a.id: a for a in _build_agents()}

# ─────────────────────────────────────────────
# MCP Tool Configuration
# ─────────────────────────────────────────────

MAX_TOOL_CALLS_PER_AGENT = 8              # Max incremental tool calls per agent per day

MCP_TOOLS = {
    "screen_stocks": {
        "source": "Alpha Vantage",
        "description": "Screen stocks by fundamentals, technicals, and sector",
    },
    "get_technicals": {
        "source": "Alpha Vantage / yfinance",
        "description": "Get SMA-20, SMA-50, SMA-200, RSI, and OHLCV history for a ticker",
    },
    "get_short_interest": {
        "source": "FINRA",
        "description": "Get short sale volume and days to cover for a ticker",
    },
    "get_market_news": {
        "source": "Finnhub",
        "description": "Get today's market headlines and ticker-specific news",
    },
    "get_fundamentals": {
        "source": "Alpha Vantage / FMP",
        "description": "Get P/E, EV/EBITDA, revenue, earnings, market cap for a ticker",
    },
    "get_macro": {
        "source": "FRED",
        "description": "Get macro indicators: DGS10 (10Y yield), VIXCLS (VIX)",
    },
    "get_sec_filings": {
        "source": "SEC EDGAR",
        "description": "Get recent 8-K, 10-Q, Form 4 filings for a company",
    },
    "web_search": {
        "source": "Brave Search API",
        "description": "General web search for financial research and catalyst discovery",
    },
    "fetch_url": {
        "source": "Custom (sanitized)",
        "description": "Read a URL and extract clean text content (HTML stripped, scripts removed)",
    },
    "propose_trades": {
        "source": "Local",
        "description": "Submit your trading decisions for today. Structured JSON output.",
    },
}

# ─────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────

import pathlib

V2_ROOT = pathlib.Path(__file__).parent
DATA_DIR = V2_ROOT / "data"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
PLAYBOOKS_DIR = DATA_DIR / "playbooks"
PORTFOLIOS_DIR = DATA_DIR / "portfolios"
LOGS_DIR = V2_ROOT / "logs"
TOOL_CALLS_DIR = LOGS_DIR / "tool_calls"
DECISIONS_DIR = LOGS_DIR / "decisions"
ADHERENCE_DIR = LOGS_DIR / "adherence"
SCHEMAS_DIR = V2_ROOT / "schemas"

# Ensure all directories exist
for d in [SNAPSHOTS_DIR, PLAYBOOKS_DIR, PORTFOLIOS_DIR,
          TOOL_CALLS_DIR, DECISIONS_DIR, ADHERENCE_DIR]:
    d.mkdir(parents=True, exist_ok=True)
