"""
Update performance.csv with S&P 500 (SPY) baseline.
Shows what $1,000 invested in SPY on the start date would be worth each day.
"""

import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime, timedelta

# Configuration
INITIAL_CAPITAL = 1000
LOGS_DIR = Path(__file__).parent.parent / "logs"
PERFORMANCE_CSV = LOGS_DIR / "performance.csv"


def fetch_spy_data(start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch SPY closing prices for the date range."""
    # Add buffer day before start to get initial price
    start_dt = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=5)
    end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
    
    print(f"📊 Fetching SPY data from {start_dt.date()} to {end_dt.date()}...")
    
    spy = yf.Ticker("SPY")
    hist = spy.history(start=start_dt.strftime("%Y-%m-%d"), end=end_dt.strftime("%Y-%m-%d"))
    
    if hist.empty:
        raise ValueError("No SPY data returned from Yahoo Finance")
    
    # Keep only closing prices
    hist = hist[['Close']].reset_index()
    hist['Date'] = hist['Tz Localize'].dt.strftime("%Y-%m-%d") if 'Tz Localize' in hist.columns else hist['Date'].dt.strftime("%Y-%m-%d")
    hist = hist.rename(columns={'Close': 'SPY_Close'})
    
    return hist[['Date', 'SPY_Close']]


def calculate_baseline(performance_df: pd.DataFrame, spy_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate what $1,000 invested in SPY would be worth on each date."""
    
    # Get the start date from performance data
    start_date = performance_df['Date'].iloc[0]
    print(f"📅 Experiment start date: {start_date}")
    
    # Merge SPY data with performance dates
    merged = performance_df.merge(spy_df, on='Date', how='left')
    
    # Forward-fill for weekends/holidays
    merged['SPY_Close'] = merged['SPY_Close'].ffill()
    
    # Get initial SPY price (price on or just before start date)
    spy_on_start = spy_df[spy_df['Date'] <= start_date]['SPY_Close'].iloc[-1]
    print(f"💰 SPY price on start: ${spy_on_start:.2f}")
    
    # Calculate shares bought with $1,000
    shares = INITIAL_CAPITAL / spy_on_start
    print(f"📈 Shares purchased: {shares:.4f}")
    
    # Calculate daily portfolio value
    merged['SP500'] = (merged['SPY_Close'] * shares).round(2)
    
    return merged.drop(columns=['SPY_Close'])


def main():
    print("=" * 50)
    print("🔄 S&P 500 BASELINE UPDATER")
    print("=" * 50)
    
    # Read existing performance data
    if not PERFORMANCE_CSV.exists():
        print("❌ performance.csv not found!")
        return
    
    df = pd.read_csv(PERFORMANCE_CSV)
    print(f"📂 Loaded {len(df)} rows from performance.csv")
    
    # Get date range
    start_date = df['Date'].iloc[0]
    end_date = df['Date'].iloc[-1]
    
    # Fetch SPY data
    try:
        spy_data = fetch_spy_data(start_date, end_date)
    except Exception as e:
        # Try alternative column name
        spy = yf.Ticker("SPY")
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=5)
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        hist = spy.history(start=start_dt.strftime("%Y-%m-%d"), end=end_dt.strftime("%Y-%m-%d"))
        hist = hist[['Close']].reset_index()
        hist['Date'] = pd.to_datetime(hist['Date']).dt.strftime("%Y-%m-%d")
        spy_data = hist.rename(columns={'Close': 'SPY_Close'})[['Date', 'SPY_Close']]
    
    print(f"✅ Got {len(spy_data)} days of SPY data")
    
    # Calculate baseline
    updated_df = calculate_baseline(df, spy_data)
    
    # Show preview
    print("\n📊 Preview (last 5 rows):")
    print(updated_df.tail().to_string(index=False))
    
    # Save updated CSV
    updated_df.to_csv(PERFORMANCE_CSV, index=False)
    print(f"\n✅ Updated {PERFORMANCE_CSV}")
    
    # Show final values
    latest = updated_df.iloc[-1]
    print(f"\n📈 Latest Values ({latest['Date']}):")
    for col in ['ChatGPT', 'Gemini', 'Claude', 'Perplexity', 'SP500']:
        if col in latest:
            val = latest[col]
            change = ((val - INITIAL_CAPITAL) / INITIAL_CAPITAL * 100)
            emoji = "🟢" if change >= 0 else "🔴"
            print(f"   {emoji} {col}: ${val:,.2f} ({change:+.2f}%)")


if __name__ == "__main__":
    main()
