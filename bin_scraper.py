from help_functions import get_coins_list, client, Kline, print_ichimoku, get_time
from config import time_dict
from binance.client import Client
import matplotlib.pyplot as plt
from sql import create_markets_databases, insert_klines
from datetime import datetime
import numpy as np

#sample input
t_now = datetime.now()
time_frame = ('4H',)
time_interval = ('1 month ago UTC',)
markets_filtered = get_coins_list()
idx = markets_filtered.index('NCASHBTC')
markets_filtered = get_coins_list()[idx: idx+1]
moon_coins = ['VIBE', 'VIB', 'FUEL', 'WPR', 'POWR', 'CND', 'FUN',
              'ADX', 'WAVES', 'APPC', 'MTH', 'STORM', 'MOD', 'THETA',
              'REQ', 'TNT', 'DATA', 'DNT', 'STORJ', 'ZIL', 'LEND', 'CLOAK']
# create_markets_databases(markets_filtered, time_frame)


def get_klines(markets, frame=time_frame, interval=time_interval, include_vol=False, insert_data=False):
    for tf in frame:
        for ti in interval:
            for market in markets:
                tf_t = getattr(Client, time_dict[tf])
                all_klines = []

                fig, axs = plt.subplots(2, 1, figsize=(30,10), gridspec_kw = {'height_ratios':[5, 1]}, sharex=True)
                print(f'Generating data for {market}_{tf}...')
                data = client.get_historical_klines_generator(symbol=market,
                                                                    interval=tf_t,
                                                                    start_str=ti)
                # todo - get data from sql server - if the data is obsolete, update from the exchange

                [all_klines.append(Kline(*kline)) for kline in data]
                time = get_time(all_klines)
                bool_filter = plot_wicks(all_klines, axs, time)
                print(f'{market}_{tf} data has been generated.')

                try:
                    print(f'Generating an ichimoku cloud plot for {market}...')
                    print_ichimoku(all_klines, time, axs, plot_lines=True)
                    print(f'Ichimoku cloud for {market} has been plotted.\n')
                except ValueError as e:
                    print(f'Something went wrong. Error: {e}\n')
                    continue
                except IndexError as e:
                    print(f'Something went wrong. Error: {e}\n')
                    continue

                if include_vol:
                    vol = np.array([w.volume for w in all_klines])
                    plot_vol(all_klines, axs, vol, bool_filter)

                axs[0].set_xlabel('time', fontsize=14)
                axs[0].set_title(f'{market} market', fontsize=20)
                plt.show()
                fig.savefig(f'plots//{market}_{tf}.png', bbox_inches='tight')

                if insert_data:
                    db_name = f'{market}_{tf_t}'.lower()
                    insert_klines(all_klines, db_name)


def plot_wicks(klines, axs, time):
    close_prices = [w.close_price for w in klines]
    a = np.array(close_prices[:-1])
    b = np.array(close_prices[1:])
    is_greater = np.insert(a > b, 0, True)

    low_price, high_price, open_price, close_price = [], [], [], []
    [(low_price.append(w.low_price),
     high_price.append(w.high_price),
     close_price.append(w.close_price),
     open_price.append(w.open_price))
     for w in klines]

    time = np.array(time)
    low_price = np.array(low_price)
    high_price = np.array(high_price)
    open_price = np.array(open_price)
    close_price = np.array(close_price)
    axs[0].vlines(time[is_greater], low_price[is_greater], high_price[is_greater], color='r', lw=1)
    axs[0].vlines(time[is_greater], open_price[is_greater], close_price[is_greater], color='r', lw=10)
    axs[0].vlines(time[~is_greater], low_price[~is_greater], high_price[~is_greater], color='g', lw=1)
    axs[0].vlines(time[~is_greater], open_price[~is_greater], close_price[~is_greater], color='g', lw=10)
    return is_greater


def plot_vol(klines, axs, vol, bool_filter):
    max_val = np.max(vol)
    x, y = [], []
    [(x.append(w.open_t), y.append(w.volume/max_val)) for w in klines]
    axs[1].set_ylabel('volume', fontsize=14)
    axs[1].vlines(np.array(x)[bool_filter], 0, np.array(y)[bool_filter], color='r', lw=5)
    axs[1].vlines(np.array(x)[~bool_filter], 0, np.array(y)[~bool_filter], color='g', lw=5)
    axs[1].set_ylim([0, 1])


# function call
get_klines(markets_filtered, time_frame, time_interval, include_vol=True)

# performance check
t_then = datetime.now()
elapsed_time = t_then - t_now
print(f'It took {elapsed_time.total_seconds()} seconds to run this program')
