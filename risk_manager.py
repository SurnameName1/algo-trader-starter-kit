"""
Risk controls. This is the part that keeps an unattended bot from doing
something stupid while you're out running errands. Do not remove these
checks to "make the bot trade more" - that's how accounts blow up.
"""
import logging

from config import Config

log = logging.getLogger("risk")


class RiskManager:
    def __init__(self):
        self.start_of_day_equity = None
        self.halted_for_day = False

    def set_start_of_day_equity(self, equity: float):
        self.start_of_day_equity = equity
        self.halted_for_day = False

    def check_daily_loss_limit(self, current_equity: float) -> bool:
        """Returns True if trading should continue, False if we've hit the daily loss cap."""
        if self.start_of_day_equity is None:
            self.set_start_of_day_equity(current_equity)
            return True

        loss_pct = (self.start_of_day_equity - current_equity) / self.start_of_day_equity
        if loss_pct >= Config.DAILY_LOSS_LIMIT_PCT:
            if not self.halted_for_day:
                log.warning(
                    f"Daily loss limit hit ({loss_pct:.1%} >= {Config.DAILY_LOSS_LIMIT_PCT:.1%}). "
                    "Halting all new trades until tomorrow."
                )
            self.halted_for_day = True
            return False
        return True

    def calculate_position_size(self, account_equity: float, price: float) -> int:
        """Caps any single position at MAX_POSITION_PCT of account equity."""
        max_dollars = account_equity * Config.MAX_POSITION_PCT
        qty = int(max_dollars // price)
        return max(qty, 0)

    def hit_stop_loss(self, entry_price: float, current_price: float) -> bool:
        if entry_price <= 0:
            return False
        drop_pct = (entry_price - current_price) / entry_price
        return drop_pct >= Config.STOP_LOSS_PCT
