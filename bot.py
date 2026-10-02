"""
Main entry point. Run this with: python bot.py

Loop, once per CHECK_INTERVAL_MINUTES, for each symbol:
  1. Check the daily loss limit. If hit, skip trading entirely today.
  2. Pull recent price bars.
  3. Ask the strategy for a BUY / SELL / HOLD signal.
  4. If BUY and we don't already hold a position: size it via risk manager, submit order.
  5. If SELL and we hold a position: close it.
  6. Also check open positions against the stop-loss on every cycle.
"""
import logging
import time
import schedule
from alpaca.trading.enums import OrderSide

from config import Config
from broker import Broker
from strategy import get_signal
from risk_manager import RiskManager
from alpaca.trading.client import TradingClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("bot")

# Tracks the price we bought at, per symbol, purely in memory for stop-loss checks.
entry_prices = {}



_clock_client = TradingClient(
    api_key=Config.API_KEY,
    secret_key=Config.SECRET_KEY,
    paper=Config.PAPER,
)


def market_is_open() -> bool:
    """True only if Alpaca says the US market is open right now."""
    clock = _clock_client.get_clock()
    if clock.is_open:
        return True
    log.info(
        f"Market closed. Next open: {clock.next_open} | Next close: {clock.next_close}"
    )
    return False

def run_cycle(broker: Broker, risk: RiskManager):
    if not market_is_open():
        return

    equity = broker.get_account_equity()
    log.info(f"Account equity: ${equity:,.2f}")

    if not risk.check_daily_loss_limit(equity):
        return  # Daily loss cap hit - do nothing until tomorrow.

    for symbol in Config.SYMBOLS:
        try:
            process_symbol(symbol, broker, risk)
        except Exception as e:
            log.exception(f"Error processing {symbol}: {e}")


def process_symbol(symbol: str, broker: Broker, risk: RiskManager):
    bars = broker.get_recent_bars(symbol)
    if bars.empty:
        log.warning(f"No price data for {symbol}, skipping.")
        return

    current_price = float(bars["close"].iloc[-1])
    held_qty = broker.get_open_position_qty(symbol)

    # Stop-loss check happens regardless of the strategy signal.
    if held_qty > 0 and symbol in entry_prices:
        if risk.hit_stop_loss(entry_prices[symbol], current_price):
            log.warning(f"Stop-loss triggered for {symbol} at {current_price}. Selling.")
            broker.submit_market_order(symbol, held_qty, OrderSide.SELL)
            entry_prices.pop(symbol, None)
            return

    signal = get_signal(bars)
    log.info(f"{symbol}: price={current_price:.2f} signal={signal} held_qty={held_qty}")

    if signal == "BUY" and held_qty == 0:
        equity = broker.get_account_equity()
        qty = risk.calculate_position_size(equity, current_price)
        if qty > 0:
            broker.submit_market_order(symbol, qty, OrderSide.BUY)
            entry_prices[symbol] = current_price
        else:
            log.info(f"Position size for {symbol} rounded to 0, skipping buy.")

    elif signal == "SELL" and held_qty > 0:
        broker.submit_market_order(symbol, held_qty, OrderSide.SELL)
        entry_prices.pop(symbol, None)


def main():
    Config.validate()
    log.info(f"Starting bot | PAPER TRADING = {Config.PAPER} | symbols = {Config.SYMBOLS}")

    broker = Broker()
    risk = RiskManager()
    risk.set_start_of_day_equity(broker.get_account_equity())

    run_cycle(broker, risk)  # Run once immediately on startup.
    schedule.every(Config.CHECK_INTERVAL_MINUTES).minutes.do(run_cycle, broker, risk)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
