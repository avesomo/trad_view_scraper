from binance.client import Client
from config import API_KEY, API_SECRET
from program import get_tick
from datetime import datetime

client = Client(API_KEY, API_SECRET)
coins_list = ['DNTBTC', 'DLTBTC', 'OAXBTC', 'POLYBTC', 'GOBTC', 'GRSBTC', 'DGDBTC']
quantity= '0.05'
price= '0.00000329'
print(get_tick(['EMA100'], 'BTCUSDT', '1D'))


order = False
while not order:
    for coin in coins_list:
        coin_klines = client.get_historical_klines(symbol=coin,
                                                   interval='30m',
                                                   start_str="1 hour ago UTC")
        current_price = float(coin_klines[-1][4])
        prev_price = float(coin_klines[-2][4])

        # todo-implement a check for tickers
        # sma100, ema100 = get_tick(['SMA100', 'EMA100'], coin, '1D')

    # if (float(coin[-1][4]) - coin(BTC[-2][4])) > 500:
    #     print('Buyyy')
    #     client.order_market_buy(symbol=symbol, quantity=quantity)
    #     order = True
    # elif (float(BTC[-1][4]) - float(BTC[-2][4])) < -500:
    #     print('Sellll')
    #     client.order_market_buy(symbol=symbol, quantity=quantity)
    #     order = True
    # else:
    #     print('Do nothing')
    # sleep(10)
    order = True
