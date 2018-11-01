from help_functions import get_coins_list, client, Kline, print_ichimoku, get_time, calls_list, plot_gmma, plot_wicks, \
                           plot_vol, organize_calls, update_excel
from config import time_dict
from binance.client import Client
import matplotlib.pyplot as plt
from sql import create_markets_databases, insert_klines
import numpy as np
from datetime import datetime


#sample input
t_now = datetime.now()
time_frame = ('4H', '1D')
time_interval = ('2 month ago UTC',)
markets_filtered = get_coins_list()

# # uncomment if you want to have a specific coin plot only
# idx = markets_filtered.index('NCASHBTC')
# markets_filtered = get_coins_list()[idx:idx+1]

# part purely for future decisions ;)
# moon_coins = ['VIBE', 'VIB', 'FUEL', 'WPR', 'POWR', 'CND', 'FUN',
#               'ADX', 'WAVES', 'APPC', 'MTH', 'STORM', 'MOD', 'THETA',
#               'REQ', 'TNT', 'DATA', 'DNT', 'STORJ', 'ZIL', 'LEND', 'CLOAK',
#               'SNGLS']
# coinz = ['ADX', 'AMB', 'ARN', 'BQX', 'BRD', 'BTG', 'DASH', 'DGD', 'EVX', 'FUN', 'IOST', 'NANO', 'OAX', 'POWR', 'REQ',
#          'SALT', 'STRAT', 'VIBE', 'ZIL']

# optional - todo - focusing first on the calls - will later implement a SQLdb<>program_data exchange
# create_markets_databases(markets_filtered, time_frame)


def get_klines(markets, frame=time_frame, interval=time_interval, include_vol=False, insert_data=False, gmma=True):
    for tf in frame:
        for ti in interval:
            for market in markets:
                tf_t = getattr(Client, time_dict[tf])
                all_klines = []

                # todo - no_vol function doesnt work so far as axs items do not support indexing if less than 2 axs
                if include_vol:
                    fig, axs = plt.subplots(2, 1, figsize=(30,10), gridspec_kw = {'height_ratios':[5, 1]}, sharex=True)
                else:
                    fig, axs = plt.subplots(1, 1, figsize=(30, 10))

                print(f'Generating data for {market}_{tf}...')
                # todo - get data from sql server - if the data is obsolete, update from the exchange
                data = client.get_historical_klines_generator(symbol=market,
                                                              interval=tf_t,
                                                              start_str=ti)
                [all_klines.append(Kline(*kline)) for kline in data]
                time = get_time(all_klines)
                bool_filter = plot_wicks(all_klines, axs, time)
                print(f'{market}_{tf} data has been generated.')

                try:
                    print(f'Generating an ichimoku cloud plot for {market}...')
                    print_ichimoku(all_klines, time, axs, market, plot_lines=True)
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

                if gmma:
                    plot_gmma(axs, all_klines, time)

                current_close = all_klines[-1].close_price
                axs[0].text(time[-1], current_close, f'{current_close:.8f}', fontsize=12)
                axs[0].set_xlabel('time', fontsize=14)
                axs[0].set_title(f'{market} market', fontsize=20)

                # plt.show() # optional
                fig.savefig(f'plots//{market}_{tf}.png', bbox_inches='tight')
                plt.cla()
                plt.close()

                # optional - inserts data to sql_database
                if insert_data:
                    db_name = f'{market}_{tf_t}'.lower()
                    insert_klines(all_klines, db_name)


# main function call
get_klines(markets_filtered, time_frame, time_interval, include_vol=True)
print(calls_list)

# move called coin plots to seperate folders
organize_calls(calls_list)

# optional - create excel file containing prices for called coins
update_excel('coins.xlsx', calls_list)

# performance check
t_then = datetime.now()
elapsed_time = t_then - t_now
print(f'It took {elapsed_time.total_seconds()} seconds to run this program')





