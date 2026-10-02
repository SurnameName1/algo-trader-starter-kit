"""
Central place all settings are loaded from.
Everything comes from the .env file so you never hardcode secrets in code.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes")


def _get_float(name: str, default: float) -> float:
    val = os.getenv(name)
    return float(val) if val else default


def _get_int(name: str, default: int) -> int:
    val = os.getenv(name)
    return int(val) if val else default


class Config:
    API_KEY = os.getenv("ALPACA_API_KEY", "")
    SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
    PAPER = _get_bool("ALPACA_PAPER", True)
    DRY_RUN = _get_bool("DRY_RUN", True)
    SYMBOLS = [s.strip().upper() for s in os.getenv("SYMBOLS", "AAPL").split(",") if s.strip()]

    SHORT_WINDOW = _get_int("SHORT_WINDOW", 20)
    LONG_WINDOW = _get_int("LONG_WINDOW", 50)
    TREND_WINDOW = _get_int("TREND_WINDOW", 200)
    LOOKBACK_DAYS = _get_int("LOOKBACK_DAYS", 120)

    MAX_POSITION_PCT = _get_float("MAX_POSITION_PCT", 0.10)      # max % of account per position
    STOP_LOSS_PCT = _get_float("STOP_LOSS_PCT", 0.03)            # sell if position drops this much
    DAILY_LOSS_LIMIT_PCT = _get_float("DAILY_LOSS_LIMIT_PCT", 0.05)  # halt bot for the day past this loss

    CHECK_INTERVAL_MINUTES = _get_int("CHECK_INTERVAL_MINUTES", 15)

    @classmethod
    def validate(cls):
        problems = []
        if not cls.API_KEY or "your_paper_api_key" in cls.API_KEY:
            problems.append("ALPACA_API_KEY is missing or still the placeholder value.")
        if not cls.SECRET_KEY or "your_paper_secret_key" in cls.SECRET_KEY:
            problems.append("ALPACA_SECRET_KEY is missing or still the placeholder value.")
        if cls.SHORT_WINDOW >= cls.LONG_WINDOW:
            problems.append("SHORT_WINDOW must be smaller than LONG_WINDOW.")
        if not cls.PAPER:
            problems.append(
                "ALPACA_PAPER is set to false — this would trade with REAL money. "
                "Refusing to start until you set it back to true, or explicitly confirm you understand."
            )
        if problems:
            raise SystemExit("Config problems found:\n- " + "\n- ".join(problems))
