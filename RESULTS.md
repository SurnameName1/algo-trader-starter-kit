# Backtest Results


This document reports the honest performance of the two strategies included
in this kit. It is not a marketing document. The results are what they are.

**Read this before you buy, or before you run the bot. If you are looking for
a strategy that beats buy-and-hold on SPY, this kit does not contain one.
What it contains is an honest, tested framework — and the results prove the
framework works correctly.**

---

## Test setup

- **Symbol:** SPY
- **Starting equity:** $100,000
- **Data source:** Alpaca IEX feed (free tier)
- **Signal timing:** Completed daily bars only (no look-ahead)
- **Position sizing (backtest):** 100% of equity per position
  (the live bot uses `MAX_POSITION_PCT`, default 10%, per symbol)
- **Costs modeled:** none (paper backtest — real fills would be slightly worse)

Two strategies were tested:

1. **Regime strategy** (`get_regime_signal`)
   Long when 20-day MA > 50-day MA. Flat otherwise.

2. **Trend-filtered strategy** (`get_trend_filtered_signal`)
   Long only when 20-day MA > 50-day MA **and** price > 200-day MA. Flat otherwise.

---

## Results

### 3-year window (2023-10 → 2026-10)

| Strategy | Return | Max Drawdown | Return / DD |
|---|---|---|---|
| Regime | +33.52% | −13.03% | 2.57 |
| Buy & hold | +81.64% | −18.98% | 4.30 |

### 6-year window (2020-10 → 2026-10)

| Strategy | Return | Max Drawdown | Return / DD |
|---|---|---|---|
| Regime | +33.39% | −29.02% | 1.15 |
| Trend-filtered | +28.51% | −19.61% | 1.45 |
| Buy & hold | +127.37% | −25.38% | 5.02 |

---

## What the numbers show

**Neither strategy beats buy-and-hold on SPY.**

In every window tested:
- Absolute return was lower than simply holding SPY
- Drawdown was not meaningfully better in every case

The trend-filtered strategy reduced drawdown from −29% to −19.6% over six
years — a real improvement in risk — but gave up return in exchange. Its
return-per-unit-of-drawdown (1.45) is still well below buy-and-hold (5.02).

**The strategy has one identifiable failure mode: choppy bear markets.**

In 2022, the regime strategy took five consecutive losing trades totaling
approximately −$28,000. The 200-day trend filter reduced but did not
eliminate this problem — several whipsaws still slipped through because
SPY was oscillating around its 200-day MA.

**The strategy has one identifiable strength: avoiding clean crashes.**

Trend-following systems exit early when a sustained downtrend begins. Over
the tested windows, there was no clean crash to dodge, so this strength
never showed up. On a window including COVID (Feb–Mar 2020), the strategy
would likely have gone flat before the −30% drop.

---

## What this means for you

If you bought this kit expecting a profitable strategy, you were not
misled — but you should also not expect one. What you have is:

- A working, tested framework for building your own strategies
- A backtester that tells the truth (including when the truth is bad)
- A live bot with proper risk limits and paper-trading defaults
- Two honest reference strategies to learn from

**The value is in the framework, not the strategy.**

Anyone selling you a moving-average crossover strategy as a money-maker is
either overfitting, lying, or doesn't know what they're doing. This kit
does not do that.

---

## How to reproduce these results

1. Set up the environment (see `README.md`)
2. Open `backtest.py`
3. Adjust `start_dt` (line ~30) to control the backtest window
4. Choose the strategy by changing the import and call:
   - Regime: `from strategy import get_regime_signal`
   - Filtered: `from strategy import get_trend_filtered_signal`
5. Run: `python backtest.py`

The raw trade logs are printed on every run.

---

## Known limitations

- **Single symbol (SPY).** Results on other symbols will differ. Trend
  strategies tend to work better on commodities and crypto than on
  equity indices.
- **No transaction costs.** Real-world fills would reduce returns by
  roughly 0.05–0.2% per round-trip. For 10+ trades over six years, that's
  a small but real drag.
- **IEX data only.** Free-tier Alpaca data is from a single exchange.
  Daily closes differ slightly from the consolidated tape, but crossover
  timing is rarely affected.
- **Not walk-forward tested.** A proper walk-forward test (train on one
  period, test on another) would give more confidence. The windows tested
  here are informative but not conclusive.

---

## Version

- Kit version: 0.1
- Last tested: October 2026
- Python: 3.14
- alpaca-py: 0.44.0