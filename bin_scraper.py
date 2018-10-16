from binance.client import Client
from config import API_KEY, API_SECRET

client = Client(API_KEY, API_SECRET)
prices = client.get_all_tickers()


def get_coins_list():
    coins = [i['symbol'] for i in client.get_exchange_info()['symbols'] if 'BTC' in i['symbol']]
    return coins

# for i in tickers:
#     print(i[symbols])

# for ticker in tickers:
#     for kline in client.get_historical_klines_generator(symbol=ticker,
#                                                         interval=Client.KLINE_INTERVAL_4HOUR,
#                                                         start_str='1 day ago UTC'):
#         print(kline)

