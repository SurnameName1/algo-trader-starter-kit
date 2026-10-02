"""
Wraps all the Alpaca API calls in one place, so the rest of the bot
never has to think about the SDK directly.
"""
import logging
from datetime import datetime, timedelta

import pandas as pd
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from config import Config

log = logging.getLogger("broker")


class Broker:
    def __init__(self):
        self.trading_client = TradingClient(Config.API_KEY, Config.SECRET_KEY, paper=Config.PAPER)
        self.data_client = StockHistoricalDataClient(Config.API_KEY, Config.SECRET_KEY)

    def get_account_equity(self) -> float:
        account = self.trading_client.get_account()
        return float(account.equity)

    def get_open_position_qty(self, symbol: str) -> float:
        try:
            position = self.trading_client.get_open_position(symbol)
            return float(position.qty)
        except Exception:
            return 0.0

    def get_recent_bars(self, symbol: str, lookback_days: int = 90) -> pd.DataFrame:
        """Returns daily OHLCV bars for a symbol as a DataFrame."""
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.now() - timedelta(days=lookback_days),
        )
        bars = self.data_client.get_stock_bars(request)
        df = bars.df
        if isinstance(df.index, pd.MultiIndex):
            df = df.xs(symbol, level="symbol")
        return df

    def get_last_price(self, symbol: str) -> float:
        df = self.get_recent_bars(symbol, lookback_days=5)
        return float(df["close"].iloc[-1])

    def submit_market_order(self, symbol: str, qty: float, side: OrderSide):
        order = MarketOrderRequest(
            symbol=symbol,
            qty=qty,
            side=side,
            time_in_force=TimeInForce.DAY,
        )
        result = self.trading_client.submit_order(order)
        log.info(f"Submitted {side.value} order for {qty} {symbol} (order id {result.id})")
        return result
