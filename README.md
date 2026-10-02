# Algo Trader Starter Kit



A Python framework for building, backtesting, and running a trading

bot on Alpaca. Paper trading by default. Honest about what it does

and doesn't do.



## What this is



- A working live bot for Alpaca (paper trading)

- A backtester with drawdown and buy-and-hold comparison

- Two honest reference strategies

- Proper risk limits: position size, stop-loss, daily loss cap

- Dry-run mode so nothing ever trades accidentally



## What this is not



- A money printer

- A strategy that beats buy-and-hold on SPY (see RESULTS.md)

- Financial advice

- A system for managing real money



## Requirements



- Python 3.10 or newer

- A free Alpaca account (paper trading is free)



## Install



    python -m venv venv

    venv\Scripts\activate

    pip install -r requirements.txt

    cp .env.example .env



Then open .env and add your Alpaca paper keys.

Get them from https://app.alpaca.markets (Paper Trading dashboard).



## Verify



    python test_connection.py



## Run the bot



    python bot.py



With DRY_RUN=true (default), orders are logged, not sent.

Set DRY_RUN=false in .env to let it place paper trades.



## Run a backtest



    python backtest.py



See RESULTS.md for current results. They underperform buy-and-hold

on SPY across all tested windows. That is the honest finding.



## Project structure



    config.py         Loads settings from .env

    broker.py         Talks to Alpaca

    strategy.py       Signal logic (two strategies included)

    risk_manager.py   Position sizing and risk limits

    bot.py            Main loop

    backtest.py       Historical replay

    RESULTS.md        Honest backtest numbers

    .env.example      Settings template



## Disclaimer



For educational use. Not financial advice. Trading involves risk

of loss. The included strategies underperform buy-and-hold on SPY.

Use at your own risk.



## License



MIT - use it, modify it, sell what you build with it.




