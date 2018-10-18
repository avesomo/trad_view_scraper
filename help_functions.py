import datetime
from binance.client import Client
from config import API_KEY, API_SECRET
import matplotlib.pyplot as plt
import numpy as np

client = Client(API_KEY, API_SECRET)


class Kline:
    def __init__(self, open_time, open_price, high_price, low_price, close_price, volume,
                 close_time, quote, no_trades, taker_base, taker_quote, ignore_val):
        self.low_price = float(low_price)
        self.close_price = float(close_price)
        self.volume = float(volume)
        self.close_time = int(close_time)
        self.quote = float(quote)
        self.no_trades = int(no_trades)
        self.taker_base = float(taker_base)
        self.taker_quote = float(taker_quote)
        self.ignore_val = int(ignore_val)
        self.high_price = float(high_price)
        self.open_t = int(open_time)
        self.open_price = float(open_price)


def time_from_ts(timestamp, timespec='minutes'):
    st = datetime.datetime.fromtimestamp(timestamp / 1000)
    time = str(st.isoformat(timespec=timespec, sep=' '))
    return time


def get_coins_list():
    coins = [i['symbol'] for i in client.get_exchange_info()['symbols'] if 'BTC' in i['symbol']]
    return coins


def print_ichimoku(klines, market, axis, conv_period=20, base_period=60, span2period=120, displacement=30):
    # todo - rescale X-axis and redo subplots - they are misleading atm
    # start = klines[0].open_t
    # end = klines[-1].open_t
    time = get_time(klines)
    conversion_line = ((get_period_highs(conv_period, klines)
                       + get_period_lows(conv_period, klines))
                       / 2)
    base_line = ((get_period_highs(base_period, klines)
                 + get_period_lows(base_period, klines))
                 / 2)
    senkou_a = (conversion_line[-len(base_line):] + base_line)/2
    senkou_b = ((get_period_highs(span2period, klines)
                + get_period_lows(span2period, klines))
                / 2)
    chikou = get_chikou(displacement, klines)
    plt.plot(time[:len(chikou)], chikou, '-', linewidth=0.5, markersize=1, color='g')
    plt.plot(time[-len(conversion_line):], conversion_line, '-', linewidth=0.5, markersize=1, color='b')
    plt.plot(time[-len(base_line):], base_line, '-', linewidth=0.5, markersize=1, color='r')

    is_greater = senkou_a[-len(senkou_b):] > senkou_b
    green_a = senkou_a[-len(senkou_b):]
    green_b = senkou_b
    time_a = time[-len(senkou_b):]
    plt.fill_between(time_a[is_greater], green_a[is_greater], green_b[is_greater], color='g', alpha=0.1)
    plt.fill_between(time_a[~is_greater], green_a[~is_greater], green_b[~is_greater], color='r', alpha=0.1)

    axis.set_xlabel('time')
    axis.set_title(f'{market} market')
    # todo - rescale x-axis labels
    plt.show()


def get_period_highs(period, klines):
    period_high = []
    for i in range(period, len(klines)):
        values_high = []
        # todo- implement recursion here
        for j in klines[i - period:i]:
            values_high.append(j.open_price)
        period_high.append(np.mean(values_high))
    return np.array(period_high)


def get_period_lows(period, klines):
    period_low = []
    for i in range(period, len(klines)):
        values_low = []
        # todo- implement recursion here
        for j in klines[i - period:i]:
            values_low.append(j.open_price)
        period_low.append(np.mean(values_low))
    return np.array(period_low)


def get_chikou(period, klines):
    values_chi = [i.close_price for i in klines[period:]]
    return np.array(values_chi)


def get_time(klines):
    time_val = [i.open_t for i in klines]
    return np.array(time_val)
