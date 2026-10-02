"""
Simple moving-average crossover strategy using completed daily bars only.

Logic:
  - Ignore the newest daily bar because it may still be changing while
    the US market is open.
  - Calculate a short and long moving average from confirmed daily closes.
  - BUY when the short MA crosses above the long MA.
  - SELL when the short MA crosses below the long MA.
  - Otherwise HOLD.
"""

import logging
import pandas as pd

from config import Config

log = logging.getLogger("strategy")


def get_signal(bars: pd.DataFrame) -> str:
    """Return BUY, SELL, or HOLD using completed daily candles only."""

    # Drop the newest bar. During market hours it can be incomplete.
    completed_bars = bars.iloc[:-1].copy()

    # We need enough confirmed bars for the long MA and one previous day
    # to detect whether a crossover just happened.
    if len(completed_bars) < Config.LONG_WINDOW + 1:
        log.warning("Not enough completed price history to compute a signal.")
        return "HOLD"

    closes = completed_bars["close"]

    short_ma = closes.rolling(window=Config.SHORT_WINDOW).mean()
    long_ma = closes.rolling(window=Config.LONG_WINDOW).mean()

    prev_short = short_ma.iloc[-2]
    curr_short = short_ma.iloc[-1]
    prev_long = long_ma.iloc[-2]
    curr_long = long_ma.iloc[-1]

    if pd.isna(prev_short) or pd.isna(curr_short):
        log.warning("Moving-average values are incomplete. Holding.")
        return "HOLD"

    if pd.isna(prev_long) or pd.isna(curr_long):
        log.warning("Moving-average values are incomplete. Holding.")
        return "HOLD"

    crossed_up = prev_short <= prev_long and curr_short > curr_long
    crossed_down = prev_short >= prev_long and curr_short < curr_long

    log.info(
        f"Completed-bar MA values | "
        f"short previous={prev_short:.2f}, current={curr_short:.2f} | "
        f"long previous={prev_long:.2f}, current={curr_long:.2f}"
    )

    if crossed_up:
        return "BUY"

    if crossed_down:
        return "SELL"

    return "HOLD"



def get_regime_signal(bars: pd.DataFrame) -> str:
    """
    Regime-based signal using completed daily bars only.

    Returns:
      BUY  if short MA is above long MA (uptrend -> should be long)
      SELL if short MA is below long MA (downtrend -> should be flat)
      HOLD only if there isn't enough history yet
    """
    completed_bars = bars.iloc[:-1].copy()

    if len(completed_bars) < Config.LONG_WINDOW:
        return "HOLD"

    closes = completed_bars["close"]
    short_ma = closes.rolling(window=Config.SHORT_WINDOW).mean()
    long_ma = closes.rolling(window=Config.LONG_WINDOW).mean()

    curr_short = short_ma.iloc[-1]
    curr_long = long_ma.iloc[-1]

    if pd.isna(curr_short) or pd.isna(curr_long):
        return "HOLD"

    if curr_short > curr_long:
        return "BUY"

    return "SELL"



def get_trend_filtered_signal(bars: pd.DataFrame) -> str:
    """
    Regime signal with a 200-day trend filter.

    Only goes long when BOTH are true:
      1. short MA > long MA      (20-day > 50-day)
      2. price > 200-day SMA     (long-term uptrend)

    This avoids buying into choppy bear markets like 2022.
    """
    completed_bars = bars.iloc[:-1].copy()

    if len(completed_bars) < Config.TREND_WINDOW:
        return "HOLD"

    closes = completed_bars["close"]
    short_ma = closes.rolling(window=Config.SHORT_WINDOW).mean()
    long_ma = closes.rolling(window=Config.LONG_WINDOW).mean()
    trend_ma = closes.rolling(window=Config.TREND_WINDOW).mean()

    curr_short = short_ma.iloc[-1]
    curr_long = long_ma.iloc[-1]
    curr_trend = trend_ma.iloc[-1]
    curr_price = closes.iloc[-1]

    if pd.isna(curr_short) or pd.isna(curr_long) or pd.isna(curr_trend):
        return "HOLD"

    if curr_price > curr_trend and curr_short > curr_long:
        return "BUY"

    return "SELL"