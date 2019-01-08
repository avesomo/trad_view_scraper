from help_functions import *
from config import time_dict
from binance.client import Client
import matplotlib.pyplot as plt
from sql import create_markets_databases, insert_klines
import numpy as np
from datetime import datetime


t0 = datetime.now()
# todo-if too short interval the program hangs itself (not enough information to plot ichi cloud
TIME_FRAME = ('1H', )
TIME_INTERVAL = ('18 month ago UTC', )


def get_klines(markets, frame=TIME_FRAME, interval=TIME_INTERVAL,
               include_vol=True, insert_data=True, gmma=True,
               incl_macd=True, save_fig=False, incl_rsi=True):
    for tf in frame:
        for ti in interval:
            for market in markets:
                tf_t = getattr(Client, time_dict[tf])
                all_klines = []
                # todo - no_vol function doesnt work so far as axs items do not support indexing if less than 2 axes
                print(f'Generating data for {market}_{tf}...')
                # todo - get data from sql server - if the data is obsolete, update from the exchange
                data = client.get_historical_klines_generator(symbol=market,
                                                              interval=tf_t,
                                                              start_str=ti)
                [all_klines.append(Kline(*kline)) for kline in data]
                time_all = get_time(all_klines)
                print(f'{market}_{tf} data has been generated.')
                subplots_no = np.sum([include_vol, incl_macd, incl_rsi, 1])
                ratios = [5]
                for _ in range(subplots_no):
                    if _ > 0:
                        ratios.append(1)

                # todo-number of drawings is hardcoded now - rework
                if include_vol:
                    fig, axs = plt.subplots(subplots_no, 1, figsize=(len(all_klines)/8, 10),
                                                  gridspec_kw ={'height_ratios': ratios},
                                                  sharex=True)
                else:
                    fig, axs = plt.subplots(1, 1, figsize=(len(all_klines)/8, 10))

                try:
                    bool_filter = plot_wicks(all_klines, axs, time_all)
                    print(f'Generating an ichimoku cloud plot for {market}...')
                    senkou_a, senkou_b, d_senkou = plot_ichimoku(all_klines, time_all, axs, market, plot_lines=True)
                    print(f'Ichimoku cloud for {market} has been plotted.')
                except ValueError as e:
                    print(f'Something went wrong. Error: {e}\n')
                    continue
                except IndexError as e:
                    print(f'Something went wrong. Error: {e}\n')
                    continue
                except TypeError as e:
                    print(f'Something went wrong. Error: {e}\n')
                    continue

                current_close = all_klines[-1].close_price
                if include_vol:
                    vol = np.array([w.volume for w in all_klines])
                    plot_vol(all_klines, axs, vol, bool_filter)

                if gmma:
                    all_emas = plot_gmma(axs, all_klines, time_all)
                    gmma_x = gmma_cross(all_emas, current_close)
                    compression_shorts = gmma_compression(all_emas, current_close, ema_type=EMAS_G)
                    compression_longs = gmma_compression(all_emas, current_close)
                    if gmma_x \
                        or compression_longs \
                        or compression_shorts:
                        gmma_calls.append(market)
                        print('gmma\'s are crossing each other recently or a compression occurs!')

                if incl_macd:
                    macd_vect = plot_macd(axs, all_klines, time_all)

                if subplots_no > 1:
                    axs[0].text(time_all[-1], current_close, f'{current_close:.8f}', fontsize=12)
                    axs[0].set_xlabel('time_all', fontsize=14)
                    axs[0].set_title(f'{market} market', fontsize=20)
                else:
                    axs.text(time_all[-1], current_close, f'{current_close:.8f}', fontsize=12)
                    axs.set_xlabel('time_all', fontsize=14)
                    axs.set_title(f'{market} market', fontsize=20)

                if incl_rsi:
                    rsi_val = plot_rsi(axs, all_klines, time_all)
                # plt.show() # optional
                if save_fig:
                    fig.savefig(f'plots//{market}_{tf}.png', bbox_inches='tight')

                plt.cla()
                plt.close()

                # optional - inserts data to sql_database
                if insert_data:
                    try:
                        rsi(all_klines)
                        ema_12 = ema(all_klines, 12)
                        ema_26 = ema(all_klines, 26)
                        ema_50 = ema(all_klines, 50)
                        ema_200 = ema(all_klines, 200)
                    except IndexError as e:
                        print(f'Something went wrong. Error: {e}\n')
                        continue

                    sh_tight, long_tight, gmma_width = gmma_tightness(all_klines)
                    cloud_th = all_clouds(all_klines, senkou_a, senkou_b, DISPLACEMENT)
                    indicators = np.c_[ema_12[-len(ema_200):], ema_26[-len(ema_200):],
                                       ema_50[-len(ema_200):], ema_200[-len(ema_200):],
                                       sh_tight[-len(ema_200):], long_tight[-len(ema_200):],
                                       gmma_width[-len(ema_200):],
                                       senkou_a[-len(ema_200):], senkou_b[-len(ema_200):],
                                       d_senkou[-len(ema_200):], macd_vect[-len(ema_200):],
                                       rsi_val[-len(ema_200):], cloud_th[-len(ema_200):]]
                    db_name = f'{market}_{tf_t}'.lower()
                    insert_klines(all_klines, db_name, indicators)
                print('\n')


#sample input
markets_filtered = get_coins_list()
gmma_calls = []

# part purely for future decisions ;)
# a = 'dnt, key, ncash, adx, dlt, oax, gas, gnt, knc, lun, sngls, storj, trx, ins, via, vib'
# b = a.split(', ')
# print(b)
# markets_filtered = list(map(lambda x: x.upper()+'BTC', b))
# print(moon_coinzs)
# coinz = ['ADX', 'AMB', 'ARN', 'BQX', 'BRD', 'BTG', 'DASH', 'DGD', 'EVX', 'FUN', 'IOST', 'NANO', 'OAX',
#          'POWR', 'REQ', 'SALT', 'STRAT', 'VIBE', 'ZIL']

# # uncomment if you want to have a specific coin plot only
idx = markets_filtered.index('NEOBTC')
markets_filtered = get_coins_list()[idx:idx+1]

# optional - todo - focusing first on the calls - will later implement a SQLdb<>program_data exchange
create_markets_databases(markets_filtered, TIME_FRAME)

# main function call
get_klines(markets_filtered)

# filter calls
print(f'Cloud calls: {cloud_calls}')
print(f'GMMA calls: {gmma_calls}')

calls_filtered = set(cloud_calls).intersection(set(gmma_calls))
# gen_calls = (call for call in cloud_calls if call in gmma_calls)
# calls_filtered = [call for call in gen_calls]

print(f'Calls filtered: {calls_filtered}')

# move called coin plots to separate folders
organize_calls(calls_filtered)
organize_calls(cloud_calls, add='Cloud')
organize_calls(gmma_calls, add='GMMA')


# optional - create excel file containing prices for called coins
# update_excel('coins.xlsx', calls_filtered)
#
# performance check
t1 = datetime.now()
dt_total = t1 - t0
print(f'It took {dt_total.total_seconds()} seconds to run this program')





