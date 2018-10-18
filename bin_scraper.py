from help_functions import time_from_ts, get_coins_list, client, Kline, print_ichimoku
from binance.client import Client
import matplotlib.pyplot as plt


# todo - simplify time_frame inputs
def get_klines(markets, time_frame=Client.KLINE_INTERVAL_4HOUR, time_interval='1 day ago UTC'):
    closing = 0
    for market in markets:
        all_klines = []
        fig, vax = plt.subplots(1, 1, figsize=(30, 10))
        # todo - implement start_str into the variables
        for kline in client.get_historical_klines_generator(symbol=market,
                                                            interval=time_frame,
                                                            start_str=time_interval):

            wick = Kline(*kline)
            all_klines.append(wick)
            print(market, wick.open_price)
            # todo-print bars function
            if closing < wick.close_price:
                color = 'g'
            else:
                color = 'r'
            vax.vlines(wick.open_t, wick.low_price, wick.high_price, colors=color, lw=1)
            vax.vlines(wick.open_t, wick.open_price, wick.close_price, colors=color, lw=10)
            # todo need to normalize the prices and volume to match scales
            # vax.vlines(time_from_ts(time), 0 , volume/100000, colors=color, lw=10)
            closing = wick.close_price
        print_ichimoku(all_klines, market, vax)


# sample input
markets = get_coins_list()[3:4]
get_klines(markets, Client.KLINE_INTERVAL_4HOUR, '3 month ago UTC')
st_ts = client.get_server_time()['serverTime']
print(time_from_ts(st_ts))
