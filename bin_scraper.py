from help_functions import get_coins_list, client, Kline, print_ichimoku
from config import time_dict
from binance.client import Client
import matplotlib.pyplot as plt
from sql import create_markets_databases, insert_klines


#sample input
time_frame = ('1H',)
time_interval = ('2 month ago UTC',)
markets_filtered = get_coins_list()
idx = markets_filtered.index('BLZBTC')
markets_filtered = get_coins_list()[idx: idx+1]
# create_markets_databases(markets_filtered, time_frame)


def get_klines(markets, frame=time_frame, interval=time_interval):
    for tf in frame:
        for ti in interval:
            closing = 0
            for market in markets:
                if market == 'HSRBTC' or market == 'VENBTC' or market == 'RPXBTC':
                    continue
                tf_t = getattr(Client, time_dict[tf])
                all_klines = []
                fig, vax = plt.subplots(1, 1, figsize=(30, 10))
                print(f'Generating data for {market}_{tf}...')
                # todo - get data from sql server - if the data is obsolete, update from the exchange
                for kline in client.get_historical_klines_generator(symbol=market,
                                                                    interval=tf_t,
                                                                    start_str=ti):
                    wick = Kline(*kline)
                    all_klines.append(wick)
                    paint_wicks(wick, closing, vax)
                    closing = wick.close_price
                print(f'{market}_{tf} data has been generated.')
                print_ichimoku(all_klines, market, vax)
                fig.savefig(f'plots//{market}_{tf}.png', bbox_inches='tight')
                # db_name = f'{market}_{tf_t}'.lower()
                # insert_klines(all_klines, db_name)


def paint_wicks(wick, closing, axis):
    if closing < wick.close_price:
        color = 'g'
    else:
        color = 'r'
    axis.vlines(int(wick.open_t), wick.low_price, wick.high_price, colors=color, lw=1)
    axis.vlines(int(wick.open_t), wick.open_price, wick.close_price, colors=color, lw=10)
    # todo need to normalize the prices and volume to match scales
    # axis.vlines(time_from_ts(time), 0 , volume/100000, colors=color, lw=10)


# sample input
get_klines(markets_filtered, time_frame, time_interval)
# st_ts = client.get_server_time()['serverTime']

