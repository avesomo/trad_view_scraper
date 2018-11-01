import datetime
from binance.client import Client
from config import API_KEY, API_SECRET
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import shutil
from datetime import datetime
import openpyxl
from config import time_dict



client = Client(API_KEY, API_SECRET)
calls_list = []
displacement = 30


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


def print_ichimoku(klines, time, axs, market, conv_period=20, base_period=60, span2period=120, displacement=30,
                   plot_lines=False, plot_cloud=True):
    dist = time[1] - time[0]
    time_new = add_time(time, dist, displacement)

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
    is_greater = senkou_a[-len(senkou_b):] >= senkou_b
    time_a = time_new[-len(senkou_b):]
    current_close_price = klines[-1].close_price
    current_open_price = np.mean([k.open_price for k in klines[-3:]])

    # plotting lines - optional
    if plot_lines:
        axs[0].plot(time[:len(chikou)], chikou, '-', linewidth=1, markersize=1, color='g')
        axs[0].plot(time[-len(conversion_line):], conversion_line, '-', linewidth=1, markersize=1, color='b')
        axs[0].plot(time[-len(base_line):], base_line, '-', linewidth=1, markersize=1, color='r')
        axs[0].plot(time[:len(chikou)], chikou, '-', linewidth=1, markersize=1, color='g')

    # plotting cloud
    if plot_cloud:
        axs[0].fill_between(time_a, senkou_a[-len(senkou_b):], senkou_b, where=is_greater, color='g', alpha=0.1)
        axs[0].fill_between(time_a, senkou_a[-len(senkou_b):], senkou_b, where=~is_greater, color='r', alpha=0.1)
        axs[0].plot(time_new[-len(senkou_a):], senkou_a, '-', linewidth=0.5, markersize=1, color='g')
        axs[0].plot(time_new[-len(senkou_b):], senkou_b, '-', linewidth=0.5, markersize=1, color='r')

    cross = cloud_cross(senkou_a, senkou_b, displacement, time_a, axs)

    # senkous crossing and checks if the nearby cloud is thin enough
    if cross and is_close(senkou_a, senkou_b, current_open_price, current_close_price):
        if rad_indicator(senkou_a, senkou_b, cross, current_close_price) < 0.05:
            print(f'{market}\'s cloud is on X-roads and the cloud is thin!')
            calls_list.append(market)
            return market

    # cloud thin and price close to the cloud
    a = cloud_thickness(current_open_price, current_close_price, senkou_a, senkou_b, displacement)
    b = is_close(senkou_a, senkou_b, current_open_price, current_close_price)
    if a < 0.018 or b:
        print(f'{market}\'s cloud is thin and the price is close to it!')
        calls_list.append(market)
        return market


def plot_wicks(klines, axs, time):
    # function plots markets price diagram as bars(wicks)
    close_prices = [w.close_price for w in klines]
    a = np.array(close_prices[:-1])
    b = np.array(close_prices[1:])
    bool_filter = np.insert(a > b, 0, True)
    low_price, high_price, open_price, close_price = [], [], [], []

    [(low_price.append(w.low_price),
     high_price.append(w.high_price),
     close_price.append(w.close_price),
     open_price.append(w.open_price))
     for w in klines]

    time_np = np.array(time)
    low_price = np.array(low_price)
    high_price = np.array(high_price)
    open_price = np.array(open_price)
    close_price = np.array(close_price)
    axs[0].vlines(time_np[bool_filter], low_price[bool_filter], high_price[bool_filter], color='r', lw=1)
    axs[0].vlines(time_np[bool_filter], open_price[bool_filter], close_price[bool_filter], color='r', lw=10)
    axs[0].vlines(time_np[~bool_filter], low_price[~bool_filter], high_price[~bool_filter], color='g', lw=1)
    axs[0].vlines(time_np[~bool_filter], open_price[~bool_filter], close_price[~bool_filter], color='g', lw=10)
    return bool_filter


def plot_vol(klines, axs, vol, bool_filter):
    # function plots volume on a figure below the main one
    max_val = np.max(vol)
    x, y = [], []
    [(x.append(w.open_t), y.append(w.volume/max_val)) for w in klines]
    axs[1].set_ylabel('volume', fontsize=14)
    axs[1].vlines(np.array(x)[bool_filter], 0, np.array(y)[bool_filter], color='r', lw=5)
    axs[1].vlines(np.array(x)[~bool_filter], 0, np.array(y)[~bool_filter], color='g', lw=5)
    axs[1].set_ylim([0, 1])


def cloud_cross(senkou_a, senkou_b, displacement, time_a, axs):
    # function checks if the senkou_a(green) and senkou_b(red)
    # are soon crossing each other (or recently did)
    i = -20
    if senkou_a[i] > senkou_b[i]:
        while senkou_a[i] > senkou_b[i]:
            i -= 1
            if i == -displacement-12:
                i = None
                break
    else:
        while senkou_b[i] > senkou_a[i]:
            i -= 1
            if i == -displacement-12:
                i = None
                break
    if i:
        cross_idx = i+1
        axs[0].axvline(time_a[cross_idx])
        return cross_idx


def rad_indicator(senkou_a, senkou_b, point, close_price, steps=6):
    # func checks if the cloud is thin locally at defined point
    cloud_mean_r = np.mean(senkou_a[point:point+steps] - senkou_b[point:point+steps])
    cloud_mean_l = np.mean(senkou_a[point-steps:point] - senkou_b[point-steps:point])
    return min(cloud_mean_r/close_price, cloud_mean_l/close_price)


def cloud_thickness(open_price, close_price, senkou_a, senkou_b, disp, steps=3):
    # returns a minimum value of thickness as a % of coins current_price for further steps(wicks)
    thicknesses = []
    price = (open_price + close_price) / 2
    for i in range(1, steps+1):
        thk = abs(senkou_a[-disp+i] - senkou_b[-disp+i])
        thicknesses.append(thk)
    return min(thicknesses)/price


def is_close(senkou_a, senkou_b, open_price, close_price, point=displacement):
    # checks if the current price is close to the cloud
    limiter = max(senkou_a[-point], senkou_b[-point])
    price = (open_price+close_price)/2
    if open_price >= limiter:
        if (abs(open_price - senkou_a[-point]) < 0.025 * price) | (
                abs(open_price - senkou_b[-point]) < 0.025 * price):
            return True
        else:
            return False
    else:
        if (abs(close_price - senkou_a[-point]) < 0.025 * price) | (
                abs(close_price - senkou_b[-point]) < 0.025 * price):
            return True
        else:
            return False


def plot_gmma(axs, klines, time):
    # function plots gmma-indicator based on given emas periods
    emas_g = [3, 5, 8, 10, 12, 15]
    emas_r = [30, 35, 40, 45, 50, 60]
    for period in emas_g:
        color = 'g'
        axs[0].plot(time[period:], EMA(klines, period), '-', linewidth=1, markersize=1, color=color)
    for period in emas_r:
        color = 'r'
        axs[0].plot(time[period:], EMA(klines, period), '-', linewidth=1, markersize=1, color=color)


def SMA(klines, period):
    # func calculates and returns a SMA list-object
    period_sma = []
    for i in range(period-1, len(klines)):
        values_sma = []
        for k in klines[i-period+1:i]:
            values_sma.append(k.close_price)
        period_sma.append(np.mean(values_sma))
    return period_sma


def EMA(klines, period):
    # func calculates and returns an EMA list-object
    sma = SMA(klines, period)[0]
    multiplier = (2 / (period + 1))
    ema_values = []
    first_val = klines[period]
    ema_previous = (first_val.close_price - sma) * multiplier + sma
    ema_values.append(ema_previous)
    for i in range(period+1, len(klines)):
        ema_current = (klines[i].close_price - ema_previous) * multiplier + ema_previous
        ema_values.append(ema_current)
        ema_previous = ema_current
    return ema_values


def organize_calls(calls):
    # function moves called coins to seperate folders
    source_path = os.path.join(os.getcwd(), 'plots')
    files = os.listdir(source_path)
    current_time = time.strftime("%Y-%m-%d %H_%M")
    os.chdir(source_path)
    for coin in calls:
        directory = f'{current_time}'
        if not os.path.exists(directory):
            os.makedirs(directory)
        for f in files:
            if f.startswith(f'{coin}'):
                shutil.move(f'{f}', os.path.join(directory, f))


# todo - could recreate the function to match both highs/lows and other stuff
def get_period_highs(period, klines):
    # function returns the lowest price value at given (past) period
    period_high = []
    for i in range(period, len(klines)):
        values_high = []
        # todo- implement recursion here
        for j in klines[i - period:i]:
            values_high.append(j.high_price)
        period_high.append(np.max(values_high))
    return np.array(period_high)


def get_period_lows(period, klines):
    # function returns the lowest price value at given (past) period
    period_low = []
    for i in range(period, len(klines)):
        values_low = []
        # todo- implement recursion here
        for j in klines[i - period:i]:
            values_low.append(j.low_price)
        period_low.append(np.min(values_low))
    return np.array(period_low)


def get_chikou(period, klines):
    # function returns chikou values (closing prices at given period)
    values_chi = [i.close_price for i in klines[period:]]
    return np.array(values_chi)


def get_time(klines):
    # function returns time values for given data
    time_val = [i.open_t for i in klines]
    return np.array(time_val)


def add_time(time_list, time_amount, repeater):
    # function adds time at given displacement - necessary for proper broadcasting
    for _ in range(repeater):
        time_list = np.append(time_list, time_list[-1] + time_amount)
    return time_list


def chooma_indicator():
    # check if open_price is a little more than conv_line (more than 0.2% and less than 0.4% of open price
    pass


def baboo_indicator():
    # while True
        # todo-making new checks
        # def buy_walls_emerging
        # def buy_walls_dropping
        # def sell_walls_emerging
        # def sell_walls dropping
    pass


def vol_check():
    # whats the 24h/4h/1h vol increase/decrease
    pass


def update_excel(filename, coin_list):
    # creating/opening excel file containing current prices
    # the excel file will later be helpful at checking if the calls are working
    if os.path.isfile(filename):
        print('file exists')
        wb = openpyxl.load_workbook(filename)
        ws = wb.active
    else:
        print('File doesnt exist. Creating new one called coins.xlsx')
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Coins_table'
        ws['A1'] = 'Date/Coins'
        wb.save(filename)

    # data input to excel
    last_row = ws.max_row
    last_col = ws.max_column

    ws[f'A{last_row+1}'] = datetime.now()
    coins = {key.value: value for value, key in enumerate(list(ws.rows)[0], 2)}
    i = 1
    for coin in coin_list:

        bin_data = list(client.get_historical_klines_generator(symbol=f'{coin}BTC',
                                                               interval=getattr(Client, time_dict['4H']),
                                                               start_str='4 hours ago UTC'))[-1]
        data = Kline(*bin_data)
        if coin not in coins.keys():
            print(f'{coin} doesnt exist yet in a table - adding new column...')
            ws.cell(row=1, column=last_col+i).value = coin
            ws.cell(row=last_row+1, column=last_col+i).value = (data.open_price + data.close_price) / 2
            i += 1
        else:
            ws.cell(row=last_row+1, column=coins[coin]-1).value = (data.open_price+data.close_price)/2

    wb.save(filename)
    wb.close()
    return print(f"Excel file {filename} created/updated.")