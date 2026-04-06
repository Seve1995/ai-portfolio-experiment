"""
AI Portfolio Experiment V2 — Virtual Portfolio Simulator

Core engine that manages virtual portfolios for all agents.
Implements:
  - T+1 execution: orders placed after close, filled at next day's open ± slippage
  - OHLC-based stop-loss/take-profit: checks daily High/Low for triggers
  - Fractional shares
  - Position sizing limits (5-25% per position, max 15 positions)
  - Full audit trail of every transaction

This is the "Autonomic Nervous System" — deterministic, no LLM input accepted
after trade proposal. Code is Law.
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Data Models
# ─────────────────────────────────────────────

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class OrderStatus(Enum):
    PENDING = "PENDING"         # Waiting for next open
    FILLED = "FILLED"           # Executed
    CANCELLED = "CANCELLED"     # Limit price not met or validation failed
    REJECTED = "REJECTED"       # Failed validation

class TradeAction(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Position:
    """An active position in the portfolio."""
    ticker: str
    shares: float                          # Fractional shares allowed
    entry_price: float                     # Average entry price
    entry_date: str                        # ISO date string
    stop_loss_price: float                 # Absolute price, system-enforced
    take_profit_price: Optional[float] = None  # Optional
    current_price: float = 0.0             # Last known price
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0

    @property
    def market_value(self) -> float:
        return self.shares * self.current_price

    @property
    def cost_basis(self) -> float:
        return self.shares * self.entry_price

    def update_price(self, price: float):
        """Update current price and recalculate unrealized P&L."""
        self.current_price = price
        self.unrealized_pnl = (price - self.entry_price) * self.shares
        if self.entry_price > 0:
            self.unrealized_pnl_pct = (price - self.entry_price) / self.entry_price


@dataclass
class Transaction:
    """A completed transaction (buy or sell)."""
    date: str
    action: str                            # "BUY" or "SELL"
    ticker: str
    shares: float
    price: float                           # Fill price (with slippage)
    total: float                           # shares × price
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    reason: str = ""
    trigger: str = ""                      # "AGENT", "STOP_LOSS", "TAKE_PROFIT"
    order_type: str = "MARKET"


@dataclass
class PendingOrder:
    """An order waiting to be filled at the next open."""
    action: TradeAction
    ticker: str
    shares: float                          # Calculated by simulator
    allocation_pct: float                  # Original request (5-25%)
    order_type: OrderType
    limit_price: Optional[float] = None
    stop_loss_pct: float = 10.0            # % below entry for stop
    take_profit_pct: Optional[float] = None
    reason: str = ""
    submitted_date: str = ""


@dataclass
class DailySnapshot:
    """Portfolio state at end of day."""
    date: str
    cash: float
    positions: dict                        # ticker -> Position (as dict)
    portfolio_value: float
    daily_return: float
    cumulative_return: float
    transactions_today: list               # List of Transaction (as dict)


# ─────────────────────────────────────────────
# Portfolio Simulator
# ─────────────────────────────────────────────

class PortfolioSimulator:
    """
    Virtual portfolio engine.
    
    Lifecycle per trading day:
    1. check_stops_and_targets(ohlc_data)  — Check if any stops/TPs triggered
    2. execute_pending_orders(open_prices)  — Fill yesterday's orders at today's open
    3. submit_orders(proposed_trades)       — Validate and queue new orders
    4. mark_to_market(close_prices)         — Update portfolio value
    5. save_state()                         — Persist to disk
    """

    def __init__(self, agent_id: str, starting_capital: float, rules, data_dir: Path):
        self.agent_id = agent_id
        self.starting_capital = starting_capital
        self.rules = rules
        self.data_dir = data_dir

        # Portfolio state
        self.cash: float = starting_capital
        self.positions: dict[str, Position] = {}
        self.pending_orders: list[PendingOrder] = []
        self.transactions: list[Transaction] = []
        self.daily_snapshots: list[DailySnapshot] = []

        # Performance tracking
        self.peak_value: float = starting_capital
        self.max_drawdown: float = 0.0
        self.daily_returns: list[float] = []

        # Load existing state if available
        self._load_state()

    # ─────────────────────────────────────
    # Step 1: Check Stops & Take-Profits
    # ─────────────────────────────────────

    def check_stops_and_targets(self, ohlc_data: dict[str, dict], today: str) -> list[Transaction]:
        """
        Check if any open positions hit their stop-loss or take-profit
        using the day's High and Low prices.
        
        Args:
            ohlc_data: {ticker: {"open": x, "high": x, "low": x, "close": x}}
            today: ISO date string
            
        Returns:
            List of transactions triggered by stops/TPs.
        """
        triggered_transactions = []
        tickers_to_remove = []

        for ticker, pos in self.positions.items():
            if ticker not in ohlc_data:
                logger.warning(f"No OHLC data for {ticker}, skipping stop check")
                continue

            bar = ohlc_data[ticker]
            low = bar["low"]
            high = bar["high"]

            # Check STOP-LOSS: triggered if Low ≤ stop_loss_price
            if low <= pos.stop_loss_price:
                fill_price = pos.stop_loss_price  # Fill at stop price (conservative)
                fill_price *= (1 - self.rules.slippage_pct)  # Apply slippage (worse for seller)

                txn = Transaction(
                    date=today,
                    action="SELL",
                    ticker=ticker,
                    shares=pos.shares,
                    price=round(fill_price, 4),
                    total=round(pos.shares * fill_price, 2),
                    reason=f"STOP-LOSS triggered (low=${low:.2f} ≤ stop=${pos.stop_loss_price:.2f})",
                    trigger="STOP_LOSS",
                )
                self.cash += txn.total
                self.transactions.append(txn)
                triggered_transactions.append(txn)
                tickers_to_remove.append(ticker)
                logger.info(f"[{self.agent_id}] STOP-LOSS {ticker}: sold {pos.shares} @ ${fill_price:.2f}")
                continue

            # Check TAKE-PROFIT: triggered if High ≥ take_profit_price
            if pos.take_profit_price and high >= pos.take_profit_price:
                fill_price = pos.take_profit_price
                fill_price *= (1 - self.rules.slippage_pct)  # Slippage

                txn = Transaction(
                    date=today,
                    action="SELL",
                    ticker=ticker,
                    shares=pos.shares,
                    price=round(fill_price, 4),
                    total=round(pos.shares * fill_price, 2),
                    reason=f"TAKE-PROFIT triggered (high=${high:.2f} ≥ tp=${pos.take_profit_price:.2f})",
                    trigger="TAKE_PROFIT",
                )
                self.cash += txn.total
                self.transactions.append(txn)
                triggered_transactions.append(txn)
                tickers_to_remove.append(ticker)
                logger.info(f"[{self.agent_id}] TAKE-PROFIT {ticker}: sold {pos.shares} @ ${fill_price:.2f}")

        for ticker in tickers_to_remove:
            del self.positions[ticker]

        return triggered_transactions

    # ─────────────────────────────────────
    # Step 2: Execute Pending Orders
    # ─────────────────────────────────────

    def execute_pending_orders(self, open_prices: dict[str, float], today: str) -> list[Transaction]:
        """
        Fill yesterday's pending orders at today's open price ± slippage.
        
        Args:
            open_prices: {ticker: open_price}
            today: ISO date string
            
        Returns:
            List of filled transactions.
        """
        filled = []

        for order in self.pending_orders:
            ticker = order.ticker
            if ticker not in open_prices:
                logger.warning(f"No open price for {ticker}, cancelling order")
                continue

            open_price = open_prices[ticker]

            # Check LIMIT orders
            if order.order_type == OrderType.LIMIT:
                if order.action == TradeAction.BUY and open_price > order.limit_price:
                    logger.info(f"[{self.agent_id}] LIMIT BUY {ticker} cancelled: open ${open_price:.2f} > limit ${order.limit_price:.2f}")
                    continue
                if order.action == TradeAction.SELL and open_price < order.limit_price:
                    logger.info(f"[{self.agent_id}] LIMIT SELL {ticker} cancelled: open ${open_price:.2f} < limit ${order.limit_price:.2f}")
                    continue

            # Apply slippage
            if order.action == TradeAction.BUY:
                fill_price = open_price * (1 + self.rules.slippage_pct)  # Pay slightly more
            else:
                fill_price = open_price * (1 - self.rules.slippage_pct)  # Receive slightly less

            fill_price = round(fill_price, 4)

            if order.action == TradeAction.BUY:
                # Recalculate shares based on current portfolio value and allocation
                portfolio_value = self._portfolio_value_at_price(open_prices)
                target_amount = portfolio_value * (order.allocation_pct / 100)
                shares = target_amount / fill_price if fill_price > 0 else 0

                # Final cash check
                cost = shares * fill_price
                if cost > self.cash:
                    shares = self.cash / fill_price
                    cost = shares * fill_price

                if shares <= 0 or cost < 1.0:
                    logger.warning(f"[{self.agent_id}] Insufficient cash for {ticker}, skipping")
                    continue

                # Calculate stop-loss and take-profit absolute prices
                stop_loss_price = round(fill_price * (1 - order.stop_loss_pct / 100), 4)
                take_profit_price = None
                if order.take_profit_pct:
                    take_profit_price = round(fill_price * (1 + order.take_profit_pct / 100), 4)

                # Execute
                self.cash -= cost

                if ticker in self.positions:
                    # Average into existing position
                    existing = self.positions[ticker]
                    total_shares = existing.shares + shares
                    avg_price = (existing.cost_basis + cost) / total_shares
                    existing.shares = total_shares
                    existing.entry_price = avg_price
                    existing.stop_loss_price = stop_loss_price  # Update stop
                    if take_profit_price:
                        existing.take_profit_price = take_profit_price
                else:
                    self.positions[ticker] = Position(
                        ticker=ticker,
                        shares=round(shares, 6),
                        entry_price=fill_price,
                        entry_date=today,
                        stop_loss_price=stop_loss_price,
                        take_profit_price=take_profit_price,
                        current_price=fill_price,
                    )

                txn = Transaction(
                    date=today,
                    action="BUY",
                    ticker=ticker,
                    shares=round(shares, 6),
                    price=fill_price,
                    total=round(cost, 2),
                    stop_loss=stop_loss_price,
                    take_profit=take_profit_price,
                    reason=order.reason,
                    trigger="AGENT",
                    order_type=order.order_type.value,
                )

            else:  # SELL
                if ticker not in self.positions:
                    logger.warning(f"[{self.agent_id}] Cannot sell {ticker}: no position")
                    continue

                pos = self.positions[ticker]
                sell_pct = order.allocation_pct / 100  # For sells, allocation_pct = % of position
                shares = pos.shares * min(sell_pct, 1.0)
                proceeds = shares * fill_price

                self.cash += proceeds
                pos.shares -= shares

                if pos.shares < 0.0001:  # Effectively zero
                    del self.positions[ticker]
                else:
                    pos.update_price(fill_price)

                txn = Transaction(
                    date=today,
                    action="SELL",
                    ticker=ticker,
                    shares=round(shares, 6),
                    price=fill_price,
                    total=round(proceeds, 2),
                    reason=order.reason,
                    trigger="AGENT",
                    order_type=order.order_type.value,
                )

            self.transactions.append(txn)
            filled.append(txn)
            logger.info(f"[{self.agent_id}] {txn.action} {txn.ticker}: {txn.shares} shares @ ${txn.price:.2f} = ${txn.total:.2f}")

        # Clear pending orders
        self.pending_orders = []
        return filled

    # ─────────────────────────────────────
    # Step 3: Submit New Orders (Validate)
    # ─────────────────────────────────────

    def submit_orders(self, proposed_trades: list[dict], today: str) -> list[dict]:
        """
        Validate proposed trades from the LLM and queue valid ones as pending orders.
        This is the validation firewall — Code is Law.
        
        Args:
            proposed_trades: List of trade dicts from propose_trades() tool call
            today: ISO date string
            
        Returns:
            List of validation results [{trade, status, reason}]
        """
        results = []
        buys_today = 0

        for trade in proposed_trades:
            action = trade.get("action", "").upper()
            ticker = trade.get("ticker", "").upper()
            allocation_pct = trade.get("allocation_pct", 0)
            order_type_str = trade.get("order_type", "MARKET").upper()
            limit_price = trade.get("limit_price")
            stop_loss_pct = trade.get("stop_loss_pct", 10)
            take_profit_pct = trade.get("take_profit_pct")
            reason = trade.get("reason", "")

            # ── Validation checks ──

            # 1. Valid action
            if action not in ("BUY", "SELL"):
                results.append({"trade": trade, "status": "REJECTED", "reason": f"Invalid action: {action}"})
                continue

            # 2. Valid ticker format
            if not ticker or len(ticker) > 5:
                results.append({"trade": trade, "status": "REJECTED", "reason": f"Invalid ticker: {ticker}"})
                continue

            # 3. Allocation bounds
            if action == "BUY":
                if allocation_pct < self.rules.min_position_pct * 100:
                    results.append({"trade": trade, "status": "REJECTED",
                                    "reason": f"Allocation {allocation_pct}% below minimum {self.rules.min_position_pct * 100}%"})
                    continue
                if allocation_pct > self.rules.max_position_pct * 100:
                    allocation_pct = self.rules.max_position_pct * 100
                    logger.warning(f"[{self.agent_id}] Capped allocation for {ticker} to {allocation_pct}%")

            # 4. Max daily buys
            if action == "BUY":
                if buys_today >= self.rules.max_daily_buys:
                    results.append({"trade": trade, "status": "REJECTED",
                                    "reason": f"Max daily buys ({self.rules.max_daily_buys}) reached"})
                    continue

            # 5. Max positions check
            if action == "BUY" and ticker not in self.positions:
                if len(self.positions) >= self.rules.max_positions:
                    results.append({"trade": trade, "status": "REJECTED",
                                    "reason": f"Max positions ({self.rules.max_positions}) reached"})
                    continue

            # 6. Long only — no shorts
            if action == "SELL" and ticker not in self.positions:
                results.append({"trade": trade, "status": "REJECTED",
                                "reason": f"Cannot sell {ticker}: no position (long-only rule)"})
                continue

            # 7. Stop-loss required for BUY
            if action == "BUY" and not stop_loss_pct:
                results.append({"trade": trade, "status": "REJECTED",
                                "reason": "Stop-loss is mandatory for all BUY orders"})
                continue

            # 8. Cash check (rough)
            if action == "BUY":
                estimated_cost = self.portfolio_value * (allocation_pct / 100)
                if estimated_cost > self.cash * 1.05:  # 5% tolerance for slippage
                    results.append({"trade": trade, "status": "REJECTED",
                                    "reason": f"Insufficient cash: need ~${estimated_cost:.0f}, have ${self.cash:.0f}"})
                    continue

            # ── Validation passed — queue order ──
            try:
                order_type = OrderType[order_type_str]
            except KeyError:
                order_type = OrderType.MARKET

            order = PendingOrder(
                action=TradeAction[action],
                ticker=ticker,
                shares=0,                  # Calculated at execution time
                allocation_pct=allocation_pct,
                order_type=order_type,
                limit_price=limit_price if order_type == OrderType.LIMIT else None,
                stop_loss_pct=stop_loss_pct,
                take_profit_pct=take_profit_pct,
                reason=reason,
                submitted_date=today,
            )
            self.pending_orders.append(order)

            if action == "BUY":
                buys_today += 1

            results.append({"trade": trade, "status": "ACCEPTED", "reason": "Order queued for T+1 execution"})
            logger.info(f"[{self.agent_id}] Queued {action} {ticker} ({allocation_pct}% {order_type_str})")

        return results

    # ─────────────────────────────────────
    # Step 4: Mark to Market
    # ─────────────────────────────────────

    def mark_to_market(self, close_prices: dict[str, float], today: str) -> DailySnapshot:
        """
        Update all position prices and compute daily performance.
        
        Args:
            close_prices: {ticker: close_price}
            today: ISO date string
            
        Returns:
            DailySnapshot with end-of-day portfolio state.
        """
        for ticker, pos in self.positions.items():
            if ticker in close_prices:
                pos.update_price(close_prices[ticker])

        # Compute portfolio value
        positions_value = sum(pos.market_value for pos in self.positions.values())
        total_value = self.cash + positions_value

        # Daily return
        if self.daily_snapshots:
            prev_value = self.daily_snapshots[-1].portfolio_value
        else:
            prev_value = self.starting_capital

        daily_return = (total_value - prev_value) / prev_value if prev_value > 0 else 0
        cumulative_return = (total_value - self.starting_capital) / self.starting_capital

        # Track drawdown
        if total_value > self.peak_value:
            self.peak_value = total_value
        current_drawdown = (self.peak_value - total_value) / self.peak_value if self.peak_value > 0 else 0
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown

        self.daily_returns.append(daily_return)

        # Build snapshot
        today_txns = [t for t in self.transactions if t.date == today]
        snapshot = DailySnapshot(
            date=today,
            cash=round(self.cash, 2),
            positions={t: asdict(p) for t, p in self.positions.items()},
            portfolio_value=round(total_value, 2),
            daily_return=round(daily_return, 6),
            cumulative_return=round(cumulative_return, 6),
            transactions_today=[asdict(t) for t in today_txns],
        )
        self.daily_snapshots.append(snapshot)

        logger.info(
            f"[{self.agent_id}] EOD: ${total_value:.2f} "
            f"({daily_return:+.2%} day, {cumulative_return:+.2%} cum) "
            f"| {len(self.positions)} positions | MDD: {self.max_drawdown:.2%}"
        )

        return snapshot

    # ─────────────────────────────────────
    # Properties
    # ─────────────────────────────────────

    @property
    def portfolio_value(self) -> float:
        """Current total portfolio value (cash + positions)."""
        positions_value = sum(pos.market_value for pos in self.positions.values())
        return self.cash + positions_value

    @property
    def num_positions(self) -> int:
        return len(self.positions)

    @property
    def position_tickers(self) -> list[str]:
        return list(self.positions.keys())

    def _portfolio_value_at_price(self, prices: dict[str, float]) -> float:
        """Calculate portfolio value using given prices."""
        val = self.cash
        for ticker, pos in self.positions.items():
            price = prices.get(ticker, pos.current_price)
            val += pos.shares * price
        return val

    # ─────────────────────────────────────
    # State Persistence
    # ─────────────────────────────────────

    def save_state(self):
        """Save portfolio state to disk."""
        state = {
            "agent_id": self.agent_id,
            "cash": round(self.cash, 2),
            "starting_capital": self.starting_capital,
            "peak_value": round(self.peak_value, 2),
            "max_drawdown": round(self.max_drawdown, 6),
            "positions": {t: asdict(p) for t, p in self.positions.items()},
            "pending_orders": [
                {
                    "action": o.action.value,
                    "ticker": o.ticker,
                    "allocation_pct": o.allocation_pct,
                    "order_type": o.order_type.value,
                    "limit_price": o.limit_price,
                    "stop_loss_pct": o.stop_loss_pct,
                    "take_profit_pct": o.take_profit_pct,
                    "reason": o.reason,
                    "submitted_date": o.submitted_date,
                }
                for o in self.pending_orders
            ],
            "daily_returns": [round(r, 6) for r in self.daily_returns],
        }
        filepath = self.data_dir / f"{self.agent_id}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)
        logger.debug(f"[{self.agent_id}] State saved to {filepath}")

    def _load_state(self):
        """Load portfolio state from disk if it exists."""
        filepath = self.data_dir / f"{self.agent_id}.json"
        if not filepath.exists():
            return

        with open(filepath, "r") as f:
            state = json.load(f)

        self.cash = state["cash"]
        self.peak_value = state.get("peak_value", self.starting_capital)
        self.max_drawdown = state.get("max_drawdown", 0.0)
        self.daily_returns = state.get("daily_returns", [])

        # Restore positions
        for ticker, pos_data in state.get("positions", {}).items():
            self.positions[ticker] = Position(**pos_data)

        # Restore pending orders
        for order_data in state.get("pending_orders", []):
            self.pending_orders.append(PendingOrder(
                action=TradeAction[order_data["action"]],
                ticker=order_data["ticker"],
                shares=0,
                allocation_pct=order_data["allocation_pct"],
                order_type=OrderType[order_data["order_type"]],
                limit_price=order_data.get("limit_price"),
                stop_loss_pct=order_data.get("stop_loss_pct", 10),
                take_profit_pct=order_data.get("take_profit_pct"),
                reason=order_data.get("reason", ""),
                submitted_date=order_data.get("submitted_date", ""),
            ))

        logger.info(f"[{self.agent_id}] State loaded: ${self.cash:.2f} cash, {len(self.positions)} positions")

    def save_snapshot_history(self):
        """Save all daily snapshots to a separate file for performance analysis."""
        filepath = self.data_dir / f"{self.agent_id}_history.json"
        with open(filepath, "w") as f:
            json.dump([asdict(s) if hasattr(s, '__dataclass_fields__') else s
                       for s in self.daily_snapshots], f, indent=2, default=str)

    def get_portfolio_summary(self) -> dict:
        """Get a human-readable summary of current portfolio state (for prompts)."""
        positions_summary = []
        for ticker, pos in self.positions.items():
            positions_summary.append({
                "ticker": ticker,
                "shares": round(pos.shares, 4),
                "entry_price": pos.entry_price,
                "current_price": pos.current_price,
                "pnl_pct": f"{pos.unrealized_pnl_pct:+.2%}",
                "market_value": round(pos.market_value, 2),
                "stop_loss": pos.stop_loss_price,
                "take_profit": pos.take_profit_price,
            })

        return {
            "agent_id": self.agent_id,
            "cash": round(self.cash, 2),
            "portfolio_value": round(self.portfolio_value, 2),
            "cumulative_return": f"{(self.portfolio_value - self.starting_capital) / self.starting_capital:+.2%}",
            "max_drawdown": f"{self.max_drawdown:.2%}",
            "num_positions": len(self.positions),
            "max_positions": self.rules.max_positions,
            "positions": positions_summary,
            "pending_orders": len(self.pending_orders),
        }
