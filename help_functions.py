import datetime
from binance.client import Client
from config import API_KEY, API_SECRET


client = Client(API_KEY, API_SECRET)


def time_from_ts(timestamp, timespec='minutes'):
    st = datetime.datetime.fromtimestamp(timestamp / 1000)
    time = str(st.isoformat(timespec=timespec, sep=' '))
    return time


def get_coins_list():
    coins = [i['symbol'] for i in client.get_exchange_info()['symbols'] if 'BTC' in i['symbol']]
    return coins
