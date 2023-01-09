import csv
import json
from datetime import datetime
from time import sleep
from concurrent.futures import ThreadPoolExecutor

import requests
from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
# from binance.cm_futures.market import trades
from celery import shared_task
from django.core.cache import cache
from binance.client import Client
from binance.spot import Spot
from binance.error import ClientError
from tradingview_ta import get_multiple_analysis, Interval

from config import Config

api_secret = 'ygb5tBtlM5XQfUcsTodjaUHihLuNMDUeK43Na9JO6p2iNffKPlncTmpscgu6RiD9'
api_key = 'OX7EVVD009ldFoCJHp7KjQwDGGj69Hp8LdAzHGLuwpj97RZFXVbLkSiWOcRupQ9y'


class MyCache:

    def __init__(self):
        self.client = Client(Config.binance_key, Config.binance_secret_key)
        self.spot = Spot()
        self.um_futures = UMFutures()

    def spot_depths(self, list_symbols):
        # todo add websocket
        # print(f'start spot: {datetime.now()}')
        result = []
        for symbol in list_symbols:

            depths = self.spot.depth(symbol=symbol)  # todo add limit 5000
            if depths['asks']:
                max_ask = max([float(ask[1]) for ask in depths['asks']])
                max_bid = max([float(bid[1]) for bid in depths['bids']])

                ask = [
                    {
                        "price": float(ask[0]),
                        "how_much_USDT": float(ask[1]) * float(ask[0]),
                        f"how_much_{symbol.replace('USDT', '')}": float(ask[1]),
                    }
                    for ask in depths['asks'] if float(ask[1]) == max_ask
                ]

                bid = [
                    {
                        "price": float(bid[0]),
                        "how_much_USDT": float(bid[1]) * float(bid[0]),
                        f"how_much_{symbol.replace('USDT', '')}": float(bid[1]),
                    }
                    for bid in depths['bids'] if float(bid[1]) == max_bid
                ]

                if float(bid[0]['how_much_USDT']) > 100000 or float(ask[0]['how_much_USDT']) > 100000:
                    price = self.spot.ticker_price(symbol)
                    result.append(
                        {
                            "lastUpdate": depths['lastUpdateId'],
                            'symbol': symbol,
                            "max_bid": bid[0],
                            "max_ask": ask[0],
                            "price": price,
                        }
                    )

        # print(f'Finish time: {datetime.now()}')
        return result

    def callback_book_depth(self, msg):
        print('ola', msg)
    def future_depth(self):

        # print(UMFuturesWebsocketClient().partial_book_depth(symbol='ethusdt', id=1, level='first', speed='speed', callback=self.callback_book_depth()))
        # print(UMFuturesWebsocketClient().diff_book_depth(symbol='ethusdt', id=1, level='first', speed='speed', callback=self.callback_book_depth))
        # print(f'start future: {datetime.now()}')
        result = []
        # print(self.um_futures.funding_rate('btcusdt'))
        _symbols = self.um_futures.exchange_info()
        symbols = [symbol['symbol'] for symbol in _symbols['symbols']]
        # print()
        for symbol in symbols:

            try:
                depths = self.um_futures.depth(symbol=symbol)  # todo add limit 5000

                if depths['asks']:
                    max_ask = max([float(ask[1]) for ask in depths['asks']])
                    max_bid = max([float(bid[1]) for bid in depths['bids']])

                    ask = [
                        {
                            "price": float(ask[0]),
                            "how_much_USDT": float(ask[1]) * float(ask[0]),
                            f"how_much_{symbol.replace('USDT', '')}": float(ask[1]),
                        }
                        for ask in depths['asks'] if float(ask[1]) == max_ask
                    ]

                    bid = [
                        {
                            "price": float(bid[0]),
                            "how_much_USDT": float(bid[1]) * float(bid[0]),
                            f"how_much_{symbol.replace('USDT', '')}": float(bid[1]),
                        }
                        for bid in depths['bids'] if float(bid[1]) == max_bid
                    ]

                    if float(bid[0]['how_much_USDT']) > 100000 or float(ask[0]['how_much_USDT']) > 100000:
                        price = self.spot.ticker_price(symbol)
                        result.append(
                            {
                                "lastUpdate": depths['lastUpdateId'],
                                'symbol': symbol,
                                "max_bid": bid[0],
                                "max_ask": ask[0],
                                "price": price,
                            }
                        )
            except ClientError as error:
                if error.status_code == 400:
                    print(f'not founded coin: {symbol}')

        # print(f'finish time: {datetime.now()}')
        return result

            # try:
            #     dept = UMFutures().depth(symbol=iu)
            #     print(dept.keys())
            # except ClientError as error:
            #     print(error.status_code, type(error.status_code))
            #     if error.status_code == 400:
            #         print(f'not founded coin: {iu}')
            #     print(iu)
            #     print(dir(error))

    def set_symbols(self):
        exchange_info = self.client.get_exchange_info()
        result = [item['symbol'] for item in exchange_info['symbols']]
        cache.set("symbols", json.dumps(result), timeout=None)

    def set_long_short_account_ratio(self, period):
        long_short_account_ratio = self.um_futures.long_short_account_ratio(period='5m', symbol='BTCUSDT')

    # @shared_task()
    def set_all(self):
        self.set_symbols()
        exchange_info = self.client.get_exchange_info()
        list_symbols = [item['symbol'] for item in exchange_info['symbols'] if
                        "USDT" in item['symbol']]  # 430 elements with 'if', 2137 elements without 'if'
        while True:
            executor = ThreadPoolExecutor(max_workers=2)
            executor.submit(self.spot_depths, list_symbols[:len(list_symbols) // 2])
            executor.submit(self.spot_depths, list_symbols[len(list_symbols) // 2:])


@shared_task()
def set_all():
    my_cache = MyCache()
    my_cache.set_symbols()
    exchange_info = my_cache.client.get_exchange_info()
    list_symbols = [item['symbol'] for item in exchange_info['symbols'] if
                    "USDT" in item['symbol']]  # 430 elements with 'if', 2137 elements without 'if'

    while True:
        executor = ThreadPoolExecutor(max_workers=3)
        a = executor.submit(my_cache.spot_depths, list_symbols[:len(list_symbols) // 2])
        b = executor.submit(my_cache.spot_depths, list_symbols[len(list_symbols) // 2:])
        result_future = executor.submit(my_cache.future_depth)
        cache.set("spot_depths", json.dumps(a.result() + b.result()), timeout=None)
        cache.set("future_depths", json.dumps(result_future.result()), timeout=None)


        # todo send to front with websocket


def buy_or_sell(what, symbol, time_frame):
    # spot = Spot()
    # price = float(spot.ticker_price(symbol)['price'])
    time = datetime.now()
    print(time)
    price = float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}").json()['price'])


    with open(f"result/{symbol}.csv", "r") as file:
        last_reader = list(csv.DictReader(file))

    if last_reader:
        last_reader = last_reader[-1]
    else:
        with open(f"result/{symbol}.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow([symbol, price, what, time_frame, time])
        return

    old_price = float(last_reader['price'])
    ten_minus = old_price - old_price * 0.02
    ten_plus = old_price * 0.02 + old_price
    if last_reader['event'] == what and ten_plus <= price >= ten_minus:
        with open(f"result/{symbol}.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow([symbol, price, what, time_frame, time])
    elif last_reader['event'] != what:
        with open(f"result/{symbol}.csv", "a") as file:
            writer = csv.writer(file)
            writer.writerow([symbol, price, what, time_frame, time])
        # if what == 'STRONG_SELL':
        #     ten = price * 0.03 - price
        #     print('STRONG_SELL')
        # else:
        #     print('STRONG_BUY')
        # if what == what and ten >= price:
        #     return
    # fild_name = ['symbol', "price", 'event', 'timeFrame', 'time']
    # with open(f"result/{symbol}.csv", "a") as file:
    #     writer = csv.writer(file)
    #     writer.writerow([symbol, price, what, time])
    # client = Client(Config.binance_key, Config.binance_secret_key)
    return f'symdol: {symbol}, price:{price}, what: {what}'

@shared_task()
def main():
    # send('Start!', broadcast=True)
    print('Start!')
    symbols = ["BINANCE:XRPUSDT", "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT"]
    while True:

        analysis = get_multiple_analysis(screener="crypto", interval=Interval.INTERVAL_1_HOUR,
                                         symbols=symbols)

        for analys in analysis:
            symbol = analysis[analys].symbol
            summary = analysis[analys].summary

            if summary['RECOMMENDATION'] == 'STRONG_SELL' or summary['RECOMMENDATION'] == 'STRONG_BUY':
                print(buy_or_sell(summary['RECOMMENDATION'], symbol, Interval.INTERVAL_15_MINUTES))
