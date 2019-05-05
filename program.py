import requests
import json
import pandas as pd
import numpy as np
from help_functions import get_coins_list


# unchangeable data from TradingView
TICKERS = {"symbols": {"tickers": ["BITFINEX:REQBTC"], "query": {"types": []}},
           "columns": ["Recommend.Other|240", "Recommend.All|240", "Recommend.MA|240", "RSI|240", "RSI[1]|240",
                       "Stoch.K|240", "Stoch.D|240", "Stoch.K[1]|240", "Stoch.D[1]|240", "CCI20|240", "CCI20[1]|240",
                       "ADX|240", "ADX+DI|240", "ADX-DI|240", "ADX+DI[1]|240", "ADX-DI[1]|240", "AO|240", "AO[1]|240",
                       "Mom|240", "Mom[1]|240", "MACD.macd|240", "MACD.signal|240", "Rec.Stoch.RSI|240",
                       "Stoch.RSI.K|240", "Rec.WR|240", "W.R|240", "Rec.BBPower|240", "BBPower|240", "Rec.UO|240",
                       "UO|240", "EMA10|240", "close|240", "SMA10|240", "EMA20|240", "SMA20|240", "EMA30|240",
                       "SMA30|240", "EMA50|240", "SMA50|240", "EMA100|240", "SMA100|240", "EMA200|240", "SMA200|240",
                       "Rec.Ichimoku|240", "Ichimoku.BLine|240", "Rec.VWMA|240", "VWMA|240", "Rec.HullMA9|240",
                       "HullMA9|240", "Pivot.M.Classic.S3|240", "Pivot.M.Classic.S2|240", "Pivot.M.Classic.S1|240",
                       "Pivot.M.Classic.Middle|240", "Pivot.M.Classic.R1|240", "Pivot.M.Classic.R2|240",
                       "Pivot.M.Classic.R3|240", "Pivot.M.Fibonacci.S3|240", "Pivot.M.Fibonacci.S2|240",
                       "Pivot.M.Fibonacci.S1|240", "Pivot.M.Fibonacci.Middle|240", "Pivot.M.Fibonacci.R1|240",
                       "Pivot.M.Fibonacci.R2|240", "Pivot.M.Fibonacci.R3|240", "Pivot.M.Camarilla.S3|240",
                       "Pivot.M.Camarilla.S2|240", "Pivot.M.Camarilla.S1|240", "Pivot.M.Camarilla.Middle|240",
                       "Pivot.M.Camarilla.R1|240", "Pivot.M.Camarilla.R2|240", "Pivot.M.Camarilla.R3|240",
                       "Pivot.M.Woodie.S3|240", "Pivot.M.Woodie.S2|240", "Pivot.M.Woodie.S1|240",
                       "Pivot.M.Woodie.Middle|240", "Pivot.M.Woodie.R1|240", "Pivot.M.Woodie.R2|240",
                       "Pivot.M.Woodie.R3|240", "Pivot.M.Demark.S1|240", "Pivot.M.Demark.Middle|240",
                       "Pivot.M.Demark.R1|240"]}
AVAIL_INTERVALS = ['|1', '|5', '|15', '|60', '|240', '', '|1W']
TIME_FRAMES_TV = ['1', '5', '15', '60', '240', '1D', '1W']
KEYS_INT = {key: tick for key, tick in zip(TIME_FRAMES_TV, AVAIL_INTERVALS)}
headers = {'User-Agent': 'Mozilla/5.0'}
url = "https://scanner.tradingview.com/crypto/scan"


def create_tick_dict(timeframe):
    ticks = {ticker.replace('|240', ''): (ticker.replace('|240', '')+KEYS_INT[timeframe], idx)
             for idx, ticker in enumerate(TICKERS['columns'])}
    return ticks


def get_ticks(markets, tickers, time_frames, print_df=False):
    result = {}
    final_dict = {}
    array_like = []
    for_removal = []

    for market in markets:
        try:
            for timeframe in time_frames:
                ticks_dict = create_tick_dict(timeframe)
                payload = {
                    "symbols": {
                        "tickers": [f"BINANCE:{market}"],
                        "query": {"types": []}
                    },
                    "columns": [ticks_dict[tick][0] for tick in tickers]
                }
                resp = requests.post(url, headers=headers, data=json.dumps(payload)).json()
                print(resp)
                res = [(tick, resp["data"][0]["d"][idx]) for idx, tick in enumerate(tickers)]
                # print(market, timeframe, res)
                for i in res:
                    array_like.append(i[1])
                result[timeframe] = res
            final_dict[market] = result

        except IndexError:
            for_removal.append(market)
            continue

    print(f'Removing non-existent markets:\n {for_removal}')
    for i in for_removal:
        markets.remove(i)

    if print_df:
        index = pd.MultiIndex.from_product([markets, time_frames],
                                           names=['Market', 'TimeFrame'])
        df = pd.DataFrame(np.array(array_like).reshape(len(time_frames)*len(markets), len(tickers)),
                          index=index,
                          columns=tickers)
        return df
    else:
        return final_dict


def get_tick(tick_names, market, timeframe, exchange="BINANCE"):
    try:
        payload = {
            "symbols": {
                "tickers": [f"{exchange}:{market}"],
                "query": {"types": []}
            },
            "columns": [tick_name+KEYS_INT[timeframe]
                        for tick_name in tick_names]
        }
        resp = requests.post(url, headers=headers, data=json.dumps(payload)).json()
        res = (resp["data"][0]["d"][i]
               for i in range(len(resp["data"][0]["d"])))
    except IndexError:
        return print('Current market does not exist on this exchange')
    return res


# # sample input
# tickers = ['SMA100', 'EMA100']
# time_frames = ['240', '1D']
# # 1D-EMA60
# markets = get_coins_list()[:20]
# df_ticks = get_ticks(markets, tickers, time_frames)
# print(df_ticks)