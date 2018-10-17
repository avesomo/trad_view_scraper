from help_functions import time_from_ts, get_coins_list, client
from binance.client import Client
import matplotlib.pyplot as plt


'''KLINES explained below
[
  [
    1499040000000,      // Open time
    "0.01634790",       // Open
    "0.80000000",       // High
    "0.01575800",       // Low
    "0.01577100",       // Close
    "148976.11427815",  // Volume
    1499644799999,      // Close time
    "2434.19055334",    // Quote asset volume
    308,                // Number of trades
    "1756.87402397",    // Taker buy base asset volume
    "28.46694368",      // Taker buy quote asset volume
    "17928899.62484339" // Ignore.
  ]
]'''


def get_klines(markets, time_frame=Client.KLINE_INTERVAL_4HOUR):
    closing = 0
    for market in markets:
        fig, vax = plt.subplots(1, 1, figsize=(10, 10))
        for kline in client.get_historical_klines_generator(symbol=market,
                                                            interval=time_frame,
                                                            start_str='1 day ago UTC'):
            print(market, kline)
            time, open_price, high_price, low_price, close_price = tuple([float(i) for i in kline[:5]])
            if closing < close_price:
                color = 'g'
            else:
                color = 'r'
            vax.vlines(time_from_ts(time), low_price, high_price, colors=color, lw=1)
            vax.vlines(time_from_ts(time), open_price, close_price, colors=color, lw=10)
            closing = close_price
            # vax.ylim(low/10, 10*high)
        vax.set_xlabel('time')
        vax.set_title(f'Vertical lines demo {market}')
        plt.show()


markets = get_coins_list()[3:4]
get_klines(markets, Client.KLINE_INTERVAL_30MINUTE)
st_ts = client.get_server_time()['serverTime']
print(time_from_ts(st_ts))
