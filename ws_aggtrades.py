from binance.client import Client
from config import API_KEY, API_SECRET
from binance.websockets import BinanceSocketManager
from datetime import datetime

client = Client(API_KEY, API_SECRET)


def process_message(msg):
    if msg['e'] == 'error':
        print('blont')
        # close and restart the socket
    else:
        print(f"{msg['E']}message type: {msg['e']}, quantity: {msg['q']},"
              f" was it seller? - {msg['m']}, price: {msg['p']}")
        # process message normally


bm = BinanceSocketManager(client, user_timeout=10)
# start any sockets here, i.e a trade socket
conn_key = bm.start_aggtrade_socket('NEOBTC', process_message)
# then start the socket manager
bm.start()


    # do something

# def is_sell(msg):
    # if msg


# msg = {
#   "e": "trade",     // Event type
#   "E": 123456789,   // Event time
#   "s": "BNBBTC",    // Symbol
#   "t": 12345,       // Trade ID
#   "p": "0.001",     // Price
#   "q": "100",       // Quantity
#   "b": 88,          // Buyer order ID
#   "a": 50,          // Seller order ID
#   "T": 123456785,   // Trade time
#   "m": true,        // Is the buyer the market maker?
#   "M": true         // Ignore
# }