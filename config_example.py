# change the filename to config.py
from configparser import ConfigParser


API_KEY = 'api_key_here'
API_SECRET = 'api_secret_here'


def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


a = {
      'KLINE_INTERVAL_1MINUTE': '1m',
      'KLINE_INTERVAL_3MINUTE': '3m',
      'KLINE_INTERVAL_5MINUTE': '5m',
      'KLINE_INTERVAL_15MINUTE': '15m',
      'KLINE_INTERVAL_30MINUTE': '30m',
      'KLINE_INTERVAL_1HOUR': '1h',
      'KLINE_INTERVAL_2HOUR': '2h',
      'KLINE_INTERVAL_4HOUR': '4h',
      'KLINE_INTERVAL_6HOUR': '6h',
      'KLINE_INTERVAL_8HOUR': '8h',
      'KLINE_INTERVAL_12HOUR': '12h',
      'KLINE_INTERVAL_1DAY': '1d',
      'KLINE_INTERVAL_3DAY': '3d',
      'KLINE_INTERVAL_1WEEK': '1w',
      'KLINE_INTERVAL_1MONTH': '1M'
}
time_dict = dict((v.upper(), k) for k, v in a.items())