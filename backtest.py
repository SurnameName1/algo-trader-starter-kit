"""
Step 2: Replay historical SPY bars through strategy.py and simulate trades.
No orders placed. Pure offline simulation.
"""
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed

from config import Config
from strategy import get_trend_filtered_signal

# Quiet the strategy logger during the backtest so output stays readable
logging.getLogger("strategy").setLevel(logging.WARNING)

load_dotenv()

api_key = os.getenv("ALPACA_API_KEY")
secret_key = os.getenv("ALPACA_SECRET_KEY")

if not api_key or not secret_key:
    raise ValueError("API keys not found in .env")

data_client = StockHistoricalDataClient(api_key=api_key, secret_key=secret_key)

symbol = "SPY"
end_dt = datetime.now()
start_dt = end_dt - timedelta(days=2190)

request = StockBarsRequest(
    symbol_or_symbols=symbol,
    timeframe=TimeFrame.Day,
    start=start_dt,
    end=end_dt,
    feed=DataFeed.IEX,
)

bars = data_client.get_stock_bars(request)
df = bars.df
if hasattr(df.index, "levels"):
    df = df.xs(symbol, level="symbol")

print(f"\n=== Backtest: {len(df)} daily bars for {symbol} ===\n")

# --- Simulation state ---
START_EQUITY = 100_000.0
POSITION_PCT = 1.0   # Backtest only: deploy full equity per position.
                     # Live bot uses Config.MAX_POSITION_PCT (0.10) per symbol.
cash = START_EQUITY
position_qty = 0
entry_price = 0.0
trades = []
equity_curve = []

# --- Replay day by day ---
for i in range(len(df)):
    # Need enough completed bars for the long SMA + one previous day
    if i < Config.LONG_WINDOW + 1:
        continue

    window = df.iloc[: i + 1]          # includes day i
    signal = get_trend_filtered_signal(window)  # drops day i internally
    price = float(df["close"].iloc[i])
    day = df.index[i]

    if signal == "BUY" and position_qty == 0:
        max_dollars = cash * POSITION_PCT
        qty = int(max_dollars // price)
        if qty > 0:
            cash -= qty * price
            position_qty = qty
            entry_price = price
            trades.append(("BUY",  str(day)[:10], price, qty))

    elif signal == "SELL" and position_qty > 0:
        cash += position_qty * price
        pnl = (price - entry_price) * position_qty
        trades.append(("SELL", str(day)[:10], price, position_qty, round(pnl, 2)))
        position_qty = 0
        entry_price = 0.0

    equity_curve.append(cash + position_qty * price)

# --- Report ---
print("Trades taken:")
if trades:
    for t in trades:
        print("  ", t)
else:
    print("  (none)")

if equity_curve:
    final_equity = equity_curve[-1]
    total_ret = (final_equity - START_EQUITY) / START_EQUITY * 100

    first_close = float(df["close"].iloc[0])
    last_close = float(df["close"].iloc[-1])
    bh_ret = (last_close - first_close) / first_close * 100

    # --- Max drawdown for the strategy ---
    peak = equity_curve[0]
    max_dd = 0.0
    for value in equity_curve:
        if value > peak:
            peak = value
        dd = (value - peak) / peak
        if dd < max_dd:
            max_dd = dd

    # --- Max drawdown for buy & hold ---
    closes = df["close"].astype(float).tolist()
    peak = closes[0]
    bh_max_dd = 0.0
    for value in closes:
        if value > peak:
            peak = value
        dd = (value - peak) / peak
        if dd < bh_max_dd:
            bh_max_dd = dd

    print(f"\nStart equity:      ${START_EQUITY:,.2f}")
    print(f"End equity:        ${final_equity:,.2f}")
    print(f"Strategy return:   {total_ret:+.2f}%")
    print(f"Buy & hold:        {bh_ret:+.2f}%")
    print(f"Strategy max DD:   {max_dd * 100:.2f}%")
    print(f"Buy & hold max DD: {bh_max_dd * 100:.2f}%")
    print(f"Open position now: {position_qty} shares of {symbol}")