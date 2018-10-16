from binance.client import Client
from config import API_KEY, API_SECRET

client = Client(API_KEY, API_SECRET)
prices = client.get_all_tickers()

for kline in client.get_historical_klines_generator("BNBBTC", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC"):
    print(kline)
