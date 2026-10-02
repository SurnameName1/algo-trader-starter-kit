import os
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient


# Load the private values from the .env file.
load_dotenv()

api_key = os.getenv("ALPACA_API_KEY")
secret_key = os.getenv("ALPACA_SECRET_KEY")
paper_trading = os.getenv("PAPER_TRADING", "true").lower() == "true"


# Stop safely if either key is missing.
if not api_key or not secret_key:
    raise ValueError(
        "API keys were not found. Check that your .env file is in this folder "
        "and contains ALPACA_API_KEY and ALPACA_SECRET_KEY."
    )


# paper=True means this connects only to your simulated paper account.
client = TradingClient(
    api_key=api_key,
    secret_key=secret_key,
    paper=paper_trading,
)


# This reads account information only. It does NOT place a trade.
account = client.get_account()

print("\nConnection successful.")
print(f"Account status: {account.status}")
print(f"Account number: {account.account_number}")
print(f"Paper trading enabled: {paper_trading}")
print(f"Cash available: ${float(account.cash):,.2f}")
print(f"Buying power: ${float(account.buying_power):,.2f}")
print(f"Total account equity: ${float(account.equity):,.2f}")
print(f"Trading blocked: {account.trading_blocked}")