"""
Trade Executor - Refactored for web use
Executes trades from text input without clipboard dependency
"""
import os
import io
import csv
import re
import time
import alpaca_trade_api as tradeapi

# --- Models ---
MODELS = {
    "1": {"name": "ChatGPT", "env_prefix": "CHATGPT"},
    "2": {"name": "Gemini", "env_prefix": "GEMINI"},
    "3": {"name": "Claude", "env_prefix": "CLAUDE"},
    "4": {"name": "Perplexity", "env_prefix": "PERPLEXITY"},
}

HEADER_MAP = {
    "TICKER": ["TICKER", "TICK", "SYMBOL"],
    "ACTION": ["ACTION", "ACT"],
    "QTY": ["QTY", "QUANTITY", "AMOUNT", "SIZE", "SHARES"],
    "TYPE": ["TYPE", "ORDER TYPE"],
    "LIMIT_PRICE": ["LIMIT_PRICE", "LIMIT PRICE", "LIMIT", "PRICE"],
    "STOP_LOSS": ["STOP_LOSS", "STOP LOSS", "STOP", "SL", "RISK MANAGEMENT", "RISK"],
    "TAKE_PROFIT": ["TAKE_PROFIT", "TAKE PROFIT", "TP", "TARGET"],
    "REASON": ["REASON", "WHY", "RATIONALE"],
}


def get_alpaca_api(model_key):
    """Returns an Alpaca REST API instance for the selected model."""
    model_info = MODELS.get(model_key)
    if not model_info:
        raise ValueError(f"Invalid model key: {model_key}")
    
    prefix = model_info['env_prefix']
    key = os.getenv(f"{prefix}_ALPACA_KEY")
    secret = os.getenv(f"{prefix}_ALPACA_SECRET")
    
    if not key or not secret:
        key = os.getenv("ALPACA_KEY")
        secret = os.getenv("ALPACA_SECRET")
        
        if not key or not secret:
            raise ValueError(f"No Alpaca API keys found for {model_info['name']}")

    base_url = "https://paper-api.alpaca.markets"
    return tradeapi.REST(key, secret, base_url, api_version="v2"), model_info


def clean_val(val, is_numeric=False):
    """Normalizes values coming from parsing. Returns None for empty/N/A fields."""
    if val is None:
        return None
    s = str(val).strip()
    s_up = s.upper().replace("$", "").replace(",", "").strip()
    if s_up in ["N/A", "NONE", "", "-"]:
        return None
    
    if is_numeric:
        dollar_match = re.search(r"\$\s*(-?\d*\.?\d+)", s_up)
        if dollar_match:
            return dollar_match.group(1)
        match = re.search(r"(-?\d*\.?\d+)", s_up)
        if match:
            return match.group(1)
            
    return s_up


def map_headers(row_keys):
    """Maps whatever headers the AI outputs to the canonical headers we support."""
    mapped = {}
    for canonical, variations in HEADER_MAP.items():
        for var in variations:
            for rk in row_keys:
                if var == rk.upper().strip():
                    mapped[canonical] = rk
                    break
            if canonical in mapped:
                break
    return mapped


def get_active_orders(api, ticker=None):
    """Fetches orders that are currently 'active' in Alpaca."""
    params = {"status": "all", "limit": 100}
    if ticker:
        params["symbols"] = [ticker]
    
    all_orders = api.list_orders(**params)
    active_statuses = {"new", "accepted", "partially_filled", "pending_new", "held"}
    return [o for o in all_orders if o.status in active_statuses]


def parse_trades(text: str, log_fn) -> list:
    """Parses the trade table from text input."""
    log_fn("📋 Parsing Portfolio Recommendation...")
    log_fn("-" * 40)

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    trades = []

    # 1) CSV MODE
    header_line_idx = None
    for i, line in enumerate(lines):
        if "ACTION" in line.upper() and "TICKER" in line.upper() and "," in line:
            header_line_idx = i
            break

    if header_line_idx is not None:
        csv_data = "\n".join(lines[header_line_idx:])
        f = io.StringIO(csv_data)
        reader = csv.DictReader(f)
        if reader.fieldnames:
            h_map = map_headers(reader.fieldnames)
            for row in reader:
                trade = {canonical: row.get(original) for canonical, original in h_map.items()}
                if trade.get("ACTION") and trade.get("TICKER"):
                    trades.append(trade)

        if trades:
            log_fn(f"🔎 Found {len(trades)} trade(s) (CSV).")
            return trades

    # 2) MARKDOWN PIPE TABLE MODE
    processed_lines = []
    for line in lines:
        if "|" in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            processed_lines.append(",".join(parts))
        else:
            processed_lines.append(line)

    header_idx = -1
    for i, line in enumerate(processed_lines):
        if any(h in line.upper() for h in ["ACTION", "TICKER"]):
            header_idx = i
            break

    if header_idx != -1:
        csv_data = "\n".join(processed_lines[header_idx:])
        f = io.StringIO(csv_data)
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if fieldnames:
            h_map = map_headers(fieldnames)
            for row in reader:
                trade = {canonical: row.get(original) for canonical, original in h_map.items()}
                if trade.get("ACTION") and trade.get("TICKER"):
                    trades.append(trade)

    if trades:
        log_fn(f"🔎 Found {len(trades)} trade(s) (Markdown table).")
        return trades

    # 3) REGEX FALLBACK
    pattern = r"(?:^|[,\s|])\s*(BUY|SELL|HOLD|CANCEL)\s*[,\s|]\s*([A-Z]+)\s*[,\s|]\s*([A-Z0-9\.]+)\s*[,\s|]\s*([A-Z\s/]+)\s*[,\s|]\s*(\$?[NA\d\.\-]+)\s*[,\s|]\s*(\$?[NA\d\.\-]+)\s*(?:[,\s|]\s*(\$?[NA\d\.\-]+))?"
    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
    for m in matches:
        trades.append({
            "ACTION": m[0].upper(),
            "TICKER": m[1].upper(),
            "QTY": m[2],
            "TYPE": m[3].upper(),
            "LIMIT_PRICE": m[4],
            "STOP_LOSS": m[5],
            "TAKE_PROFIT": m[6] if len(m) > 6 else None,
        })

    if trades:
        log_fn(f"🔎 Found {len(trades)} trade(s) (Regex fallback).")
        return trades

    log_fn("⚠️ No valid trade data found.")
    return []


def manage_hold_protection(api, ticker, stop_loss_price, log_fn, dry_run=False):
    """Manage stop-loss for HOLD positions."""
    try:
        qty = int(api.get_position(ticker).qty)
    except Exception:
        log_fn(f"   ⚠️ No open position found for {ticker} to protect.")
        return

    log_fn(f"\n🛡️ SYNCING PROTECTION: {ticker} (Target Stop: ${stop_loss_price:.2f})")

    open_orders = get_active_orders(api, ticker)
    stop_orders = [o for o in open_orders if o.side == "sell" and o.type == "stop"]
    
    conflicting_sell_orders = [
        o for o in open_orders
        if o.side == "sell" and o.type != "stop" and o.order_class != "bracket"
    ]

    if conflicting_sell_orders:
        log_fn(f"   ⚠️ Skipping STOP placement - shares reserved by standalone SELL order.")
        return

    if stop_orders:
        for order in stop_orders:
            current_stop = float(order.stop_price)
            if abs(current_stop - stop_loss_price) < 0.01:
                log_fn(f"   ✅ Already Protected: Existing stop matches ${current_stop:.2f}")
                return

            log_fn(f"   🔄 Updating stop from ${current_stop:.2f} to ${stop_loss_price:.2f}")
            if dry_run:
                log_fn(f"   [DRY RUN] Would replace stop-loss")
                return

            try:
                api.replace_order(order.id, stop_price=stop_loss_price)
                log_fn(f"   ✅ SUCCESS: Stop-loss updated.")
                return
            except Exception as e:
                log_fn(f"   ⚠️ Replace failed: {e}. Falling back to Cancel/Re-submit.")
                try:
                    api.cancel_order(order.id)
                    time.sleep(1)
                except Exception as ce:
                    log_fn(f"   ⚠️ Cancel failed: {ce}.")
                    return
    else:
        log_fn(f"   ➕ Missing Protection: No stop-loss found for {ticker}.")

    if dry_run:
        log_fn(f"   [DRY RUN] Would place stop-loss @ ${stop_loss_price:.2f}")
        return

    try:
        api.submit_order(
            symbol=ticker,
            qty=qty,
            side="sell",
            type="stop",
            time_in_force="gtc",
            stop_price=stop_loss_price,
        )
        log_fn(f"   ✅ SUCCESS: New stop-loss placed @ ${stop_loss_price:.2f}")
    except Exception as e:
        log_fn(f"   ❌ FAILED to place stop-loss: {e}")


def execute_single_trade(api, trade, log_fn, dry_run=False):
    """Execute a single trade."""
    action = clean_val(trade.get("ACTION"))
    ticker = clean_val(trade.get("TICKER"))
    qty_str = clean_val(trade.get("QTY"), is_numeric=True)
    limit_price_str = clean_val(trade.get("LIMIT_PRICE"), is_numeric=True)
    stop_loss_str = clean_val(trade.get("STOP_LOSS"), is_numeric=True)
    take_profit_str = clean_val(trade.get("TAKE_PROFIT"), is_numeric=True)

    if not action:
        return

    if action == "NO_TRADES":
        log_fn(f"📊 NO_TRADES: AI decided to stay flat today.")
        return

    if action == "HOLD":
        try:
            stop_price = float(stop_loss_str) if stop_loss_str else None
        except ValueError:
            stop_price = None

        if stop_price:
            manage_hold_protection(api, ticker, stop_price, log_fn, dry_run=dry_run)
        else:
            log_fn(f"\n✋ HOLDING: {ticker} (No stop-loss specified)")
        return

    if action == "CANCEL":
        log_fn(f"\n🚫 PROCESSING CANCEL: {ticker}")
        try:
            active_orders = get_active_orders(api, ticker)
            if not active_orders:
                log_fn(f"   ⚠️ No active orders found for {ticker}.")
                return

            log_fn(f"   🧹 Cancelling {len(active_orders)} order(s)...")
            for o in active_orders:
                if dry_run:
                    log_fn(f"   [DRY RUN] Would cancel order {o.id}")
                else:
                    api.cancel_order(o.id)
                    log_fn(f"   ✅ Cancelled order {o.id}")
        except Exception as e:
            log_fn(f"   ❌ CANCEL FAILED: {e}")
        return

    try:
        if action == "SELL":
            log_fn(f"\n📉 PROCESSING SELL: {ticker}")
            try:
                # Clear active orders first
                active_orders = get_active_orders(api, ticker)
                if active_orders:
                    log_fn(f"   🧹 Clearing {len(active_orders)} order(s) before selling.")
                    for o in active_orders:
                        if not dry_run:
                            api.cancel_order(o.id)
                    if not dry_run:
                        time.sleep(2)

                try:
                    api.get_position(ticker)
                except Exception:
                    log_fn(f"   ✅ Position already closed for {ticker}.")
                    return

                if qty_str and "ALL" in qty_str:
                    if dry_run:
                        log_fn(f"   [DRY RUN] Would close position for {ticker}.")
                    else:
                        api.close_position(ticker)
                else:
                    qty = int(qty_str) if qty_str else 0
                    if qty <= 0:
                        log_fn(f"   ⚠️ Invalid qty for SELL: {qty_str}. Skipping.")
                        return

                    if dry_run:
                        log_fn(f"   [DRY RUN] Would sell {qty} {ticker}.")
                    else:
                        api.submit_order(symbol=ticker, qty=qty, side="sell", type="market", time_in_force="day")

                log_fn(f"   ✅ SELL submitted for {ticker}")
            except Exception as e:
                log_fn(f"   ❌ SELL FAILED: {e}")
            return

        if action == "BUY":
            log_fn(f"\n🚀 PROCESSING BUY: {ticker}")

            # Ticker validity
            try:
                asset = api.get_asset(ticker)
                if not asset.tradable:
                    log_fn(f"   ❌ {ticker} is not tradable.")
                    return
            except Exception:
                log_fn(f"   ❌ Could not find {ticker}.")
                return

            # Check existing position
            try:
                pos = api.get_position(ticker)
                log_fn(f"   ⚠️ Already hold {pos.qty} shares of {ticker}. Skipping.")
                return
            except Exception:
                pass

            # Check pending buy orders
            active_orders = get_active_orders(api, ticker)
            buy_orders = [o for o in active_orders if o.side == "buy"]
            if buy_orders:
                log_fn(f"   ⚠️ Pending BUY order exists for {ticker}. Skipping.")
                return

            qty = int(qty_str) if qty_str else 0
            limit_price = float(limit_price_str) if limit_price_str else 0.0
            if qty <= 0 or limit_price <= 0:
                log_fn(f"   ⚠️ Missing qty or limit price. Skipping.")
                return

            stop_price = float(stop_loss_str) if stop_loss_str else None
            tp_price = float(take_profit_str) if take_profit_str else None

            if stop_price is not None and stop_price >= limit_price:
                log_fn(f"   ❌ STOP_LOSS >= LIMIT_PRICE. Skipping.")
                return

            account = api.get_account()
            bp = float(account.buying_power)
            est_cost = qty * limit_price
            
            log_fn(f"   Order: BUY {qty} {ticker} @ ${limit_price:.2f} (Est. ${est_cost:.2f})")

            if est_cost > bp:
                log_fn(f"   ⚠️ Insufficient buying power! Need ${est_cost:.2f}, have ${bp:.2f}")
                if not dry_run:
                    return

            params = {
                "symbol": ticker,
                "qty": qty,
                "side": "buy",
                "type": "limit",
                "time_in_force": "gtc",
                "limit_price": limit_price,
            }

            if stop_price and tp_price:
                params.update({
                    "order_class": "bracket",
                    "stop_loss": {"stop_price": stop_price},
                    "take_profit": {"limit_price": tp_price},
                })
            elif stop_price:
                params.update({"order_class": "oto", "stop_loss": {"stop_price": stop_price}})
            else:
                params["order_class"] = "simple"

            if dry_run:
                log_fn("   [DRY RUN] Would place buy order.")
            else:
                api.submit_order(**params)
                log_fn("   ✅ SUCCESS: Buy order placed!")
    except Exception as e:
        log_fn(f"   ❌ EXECUTION ERROR: {e}")


def execute_trades(model_key: str, trade_table_text: str, dry_run: bool = False) -> str:
    """
    Execute trades from the provided table text.
    
    Args:
        model_key: "1" for ChatGPT, "2" for Gemini, etc.
        trade_table_text: The AI-generated trade table
        dry_run: If True, simulate trades without executing
    
    Returns:
        Execution log as a string
    """
    logs = []
    def log_fn(msg):
        logs.append(msg)

    try:
        api, model_info = get_alpaca_api(model_key)
    except Exception as e:
        return f"❌ API Error: {e}"

    log_fn("=" * 50)
    log_fn(f"📊 TRADE EXECUTION ({model_info['name']})")
    if dry_run:
        log_fn("⚠️  DRY RUN MODE - No actual trades will be made")
    log_fn("=" * 50)

    # Print preflight status
    try:
        account = api.get_account()
        positions = api.list_positions()
        orders = get_active_orders(api)

        log_fn(f"\n💰 Equity: ${float(account.equity):,.2f}")
        log_fn(f"💸 Buying Power: ${float(account.buying_power):,.2f}")

        log_fn("\n📂 Current Positions:")
        if not positions:
            log_fn("   (No open positions)")
        else:
            for p in positions:
                log_fn(f"   • {p.symbol}: {p.qty} shares @ ${float(p.avg_entry_price):,.2f}")

        log_fn("\n📝 Open Orders:")
        if not orders:
            log_fn("   (No open orders)")
        else:
            for o in orders:
                log_fn(f"   • {o.symbol}: {o.side.upper()} {o.type.upper()} {o.qty}")
    except Exception as e:
        log_fn(f"⚠️ Could not fetch account status: {e}")

    log_fn("\n" + "=" * 50 + "\n")

    # Parse and execute trades
    trades = parse_trades(trade_table_text, log_fn)
    for t in trades:
        execute_single_trade(api, t, log_fn, dry_run=dry_run)

    log_fn("\n" + "=" * 50)
    log_fn("✅ EXECUTION COMPLETE")
    log_fn("=" * 50)

    return "\n".join(logs)
