from broker import Broker


broker = Broker()
clock = broker.trading_client.get_clock()

print("\n=== Alpaca Market Clock ===")
print(f"Market open now: {clock.is_open}")
print(f"Alpaca time: {clock.timestamp}")
print(f"Next market open: {clock.next_open}")
print(f"Next market close: {clock.next_close}")