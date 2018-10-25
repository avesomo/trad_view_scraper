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
        self.close_time = close_time
        self.quote = float(quote)
        self.no_trades = int(no_trades)
        self.taker_base = float(taker_base)
        self.taker_quote = float(taker_quote)
        self.ignore_val = int(ignore_val)
        self.high_price = float(high_price)
        self.open_t = open_time
        self.open_price = float(open_price)

    def get_attributes(self):
        return time_from_ts(self.open_t), self.open_price, self.high_price, self.low_price,\
               self.close_price, self.volume, time_from_ts(self.close_time), self.quote,\
               self.no_trades, self.taker_base, self.taker_quote, self.ignore_val


def time_from_ts(timestamp, timespec='minutes'):
    st = datetime.datetime.fromtimestamp(timestamp / 1000)
    time = str(st.isoformat(timespec=timespec, sep=' '))
    return time


def get_coins_list():
    coins = [i['symbol'] for i in client.get_exchange_info()['symbols'] if 'BTC' in i['symbol']]
    return coins


def print_ichimoku(klines, market, axis, conv_period=20, base_period=60, span2period=120, displacement=30,
                   plot_lines=False, plot_cloud=True):
    # todo - rescale X-axis, redo X/Y-axis labels
    # start = klines[0].open_t
    # end = klines[-1].open_t
    time = get_time(klines)
    dist = time[1] - time[0]
    time_new = add_time(time, dist, displacement)
    print(f'Generating an ichimoku cloud plot for {market}...')
    # todo - if the data lacks information to draw ichimoku it breaks
    # todo - implement a try-expect part

    # defining ichimoku values
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
    # plotting lines - optional
    if plot_lines:
        plt.plot(time[:len(chikou)], chikou, '-', linewidth=0.5, markersize=1, color='g')
        plt.plot(time[-len(conversion_line):], conversion_line, '-', linewidth=0.5, markersize=1, color='b')
        plt.plot(time[-len(base_line):], base_line, '-', linewidth=0.5, markersize=1, color='r')
        plt.plot(time[:len(chikou)], chikou, '-', linewidth=0.5, markersize=1, color='g')

    # plotting cloud
    if plot_cloud:
        is_greater = senkou_a[-len(senkou_b):] >= senkou_b
        time_a = time_new[-len(senkou_b):]
        plt.fill_between(time_a, senkou_a[-len(senkou_b):], senkou_b, where=is_greater, color='g', alpha=0.1)
        plt.fill_between(time_a, senkou_a[-len(senkou_b):], senkou_b, where=~is_greater, color='r', alpha=0.1)
        plt.plot(time_new[-len(senkou_a):], senkou_a, '-', linewidth=0.5, markersize=1, color='g')
        plt.plot(time_new[-len(senkou_b):], senkou_b, '-', linewidth=0.5, markersize=1, color='r')

    i = 1
    if senkou_a[-i] > senkou_b[-i]:
        while senkou_a[-i] > senkou_b[-i]:
            i += 1
        cross_time = time_a[-i+1]
    else:
        while senkou_b[-i] > senkou_a[-i]:
            i += 1
        cross_time = time_a[-i+1]

    plt.axvline(cross_time)
    if cross_time > time[-1]:
        print("Ichimoku cloud crossing soon!!!")
        # todo - do things like send e-mail, compare to TV indicators (or calculate them here)
    axis.set_xlabel('time')
    axis.set_title(f'{market} market')
    plt.show()
    return print(f'Ichimoku cloud for {market} has been plotted.')

# def check_for_crossings(senkou_a, senkou_b):

# remove one of these functions below
def get_period_highs(period, klines):
    period_high = []
    for i in range(period, len(klines)):
        values_high = []
        # todo- implement recursion here
        for j in klines[i - period:i]:
            values_high.append(j.high_price)
        period_high.append(np.max(values_high))
    return np.array(period_high)


def get_period_lows(period, klines):
    period_low = []
    for i in range(period, len(klines)):
        values_low = []
        # todo- implement recursion here
        for j in klines[i - period:i]:
            values_low.append(j.low_price)
        period_low.append(np.min(values_low))
    print(period_low)
    return np.array(period_low)


def get_chikou(period, klines):
    values_chi = [i.close_price for i in klines[period:]]
    return np.array(values_chi)


def get_time(klines):
    time_val = [i.open_t for i in klines]
    return np.array(time_val)


def add_time(time_list, time_amount, repeater):
    for _ in range(repeater):
        time_list = np.append(time_list, time_list[-1] + time_amount)
    return time_list

    # 1440000


