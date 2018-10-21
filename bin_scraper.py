from help_functions import get_coins_list, client, Kline, print_ichimoku
from config import time_dict
from binance.client import Client
import matplotlib.pyplot as plt
from sql import create_markets_databases, insert_klines


#sample input
time_frame = ('4H',)
time_interval = ('3 month ago UTC',)
markets_filtered = get_coins_list()[4:6]
create_markets_databases(markets_filtered, time_frame)


# todo - simplify time_frame inputs
def get_klines(markets, frame=time_frame, interval=time_interval):
    for tf in frame:
        for ti in interval:
            closing = 0
            for market in markets:
                tf_t = getattr(Client, time_dict[tf])
                db_name = f'{market}_{tf_t}'.lower()
                all_klines = []
                fig, vax = plt.subplots(1, 1, figsize=(30, 10))
                # todo - implement start_str into the variables
                print(f'Generating data for {market}_{tf}...')
                for kline in client.get_historical_klines_generator(symbol=market,
                                                                    interval=tf_t,
                                                                    start_str=ti):

                    wick = Kline(*kline)
                    all_klines.append(wick)
                    # todo-print bars function
                    if closing < wick.close_price:
                        color = 'g'
                    else:
                        color = 'r'
                    vax.vlines(int(wick.open_t), wick.low_price, wick.high_price, colors=color, lw=1)
                    vax.vlines(int(wick.open_t), wick.open_price, wick.close_price, colors=color, lw=10)
                    # todo need to normalize the prices and volume to match scales
                    # vax.vlines(time_from_ts(time), 0 , volume/100000, colors=color, lw=10)
                    closing = wick.close_price
                print(f'{market}_{tf} data has been generated.')
                insert_klines(all_klines, db_name)
                print_ichimoku(all_klines, market, vax)


# sample input
get_klines(markets_filtered, time_frame, time_interval)
# st_ts = client.get_server_time()['serverTime']

