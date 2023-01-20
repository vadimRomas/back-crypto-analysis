import asyncio
import json
from datetime import datetime
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_django.settings")

import django

django.setup()

import requests
from binance.depthcache import ThreadedDepthCacheManager
from binance.streams import BinanceSocketManager
from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
# from binance.cm_futures.market import trades
from celery import shared_task
from django.core.cache import cache
from binance.client import Client, AsyncClient
from binance.spot import Spot
from binance.error import ClientError
from tradingview_ta import get_multiple_analysis, Interval
from urllib3.exceptions import ProtocolError

from apps.cripto_info.models import TradingviewBot
from config import Config



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
                max_ask = max([float(ask[1]) for ask in depths['asks']])  # sell
                max_bid = max([float(bid[1]) for bid in depths['bids']])  # buy

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
                            "symbol": symbol,
                            "max_bid": bid[0],
                            "max_ask": ask[0],
                            "price": price,
                        }
                    )

        # print(f'Finish time: {datetime.now()}')
        return result

    def bot_depth(self):
        #ETHUSDT 30 minute, volume 2922.8883, ten_volume = volume * 0.005 = 14.6144415, len_ask = 17
        symbol = 'BTCUSDT'
        btc_depths = self.spot.depth(symbol, )
        # print([ask[1] for ask in btc_depths['asks'] if float(ask[1]) >= 10])

        volume = float(self.spot.klines(symbol, '30m')[-1][5])
        print(f'volume for 30 minute: {volume}')
        print(len(btc_depths['asks']))
        ten_volume = volume * 0.005 # todo try ml formuly, ask vitaliy
        print(f'{volume} * 0.001 = {ten_volume}')
        ask = [ask for ask in btc_depths['asks'] if float(ask[1]) >= ten_volume]
        print(len(ask))
        bid = [bid for bid in btc_depths['bids'] if float(bid[1]) >= ten_volume]
        return {'ask': ask, 'bid': bid}

    def callback_book_depth(self, msg):
        print('ola', msg)

    def future_depth(self):

        # print(UMFuturesWebsocketClient().partial_book_depth(symbol='ethusdt', id=1, level='first', speed='speed', callback=self.callback_book_depth()))
        # print(UMFuturesWebsocketClient().diff_book_depth(symbol='ethusdt', id=1, level='first', speed='speed', callback=self.callback_book_depth))
        # print(f'start future: {datetime.now()}')
        result = []
        print('future_depth start', datetime.now())
        # print(self.um_futures.funding_rate('btcusdt'))
        _symbols = self.um_futures.ticker_price()
        symbols = [symbol['symbol'] for symbol in _symbols]
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
                        price = self.um_futures.ticker_price(symbol)
                        result.append(
                            {
                                "lastUpdate": depths['lastUpdateId'],
                                "symbol": symbol,
                                "max_bid": bid[0],
                                "max_ask": ask[0],
                                "price": price,
                            }
                        )
            except ClientError as error:
                if error.status_code == 400:
                    print(f'not founded coin: {symbol}')

        print('future_depth finish', datetime.now())
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
    exchange_info = my_cache.spot.ticker_price()
    list_symbols = [item['symbol'] for item in exchange_info if
                    "USDT" in item['symbol']]

    # while True:
    #     executor = ThreadPoolExecutor(max_workers=3)
    #     a = executor.submit(my_cache.spot_depths, list_symbols[:len(list_symbols) // 2])
    #     b = executor.submit(my_cache.spot_depths, list_symbols[len(list_symbols) // 2:])
    #     result_future = executor.submit(my_cache.future_depth)
    #     cache.set("spot_depths", json.dumps(a.result() + b.result()), timeout=None)
    #     cache.set("future_depths", json.dumps(result_future.result()), timeout=None)


        # todo send to front with websocket


# def buy_or_sell(what, symbol, interval):
#     # spot = Spot()
#     # price = float(spot.ticker_price(symbol)['price'])
#     time = datetime.now()
#
#     sleep(0.01)
#     spot = Spot()
#     price = float(spot.ticker_price(symbol)['price'])
#
#     try:
#         with open(f"result/{symbol}-{interval}.csv", "r") as file:
#             last_reader = list(csv.DictReader(file))
#             file.close()
#     except FileNotFoundError as error:
#         with open(f"result/{symbol}-{interval}.csv", "a") as file:
#             writer = csv.writer(file)
#             writer.writerow(['symbol', "price", 'event', 'interval', 'time'])
#             writer.writerow([symbol, price, what, interval, time])
#             file.close()
#         return
#
#     if last_reader:
#         last_reader = last_reader[-1]
#     else:
#         with open(f"result/{symbol}-{interval}.csv", "a", newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow([symbol, price, what, interval, time])
#             file.close()
#         return
#
#     old_price = float(last_reader['price'])
#     ten_minus = old_price - old_price * 0.02
#     ten_plus = old_price * 0.02 + old_price
#
#     if last_reader['event'] == what and ten_plus <= price >= ten_minus:
#         with open(f"result/{symbol}-{interval}.csv", "a",
#                   newline='') as file:  # client.create_test_order(symbol=symbol, side='BUY', type='LIMIT', timeInForce='GTC', quantity=100, price=200)
#             writer = csv.writer(file)
#             writer.writerow([symbol, price, what, interval, time])
#             file.close()
#     elif last_reader['event'] != what:
#
#         with open(f"result/{symbol}-{interval}.csv", "a") as file:
#             writer = csv.writer(file)
#             writer.writerow([symbol, price, what, interval, time])
#             file.close()
#
#         # if what == 'STRONG_SELL':
#         #     ten = price * 0.03 - price
#         #     print('STRONG_SELL')
#         # else:
#         #     print('STRONG_BUY')
#         # if what == what and ten >= price:
#         #     return
#     # fild_name = ['symbol', "price", 'event', 'interval', 'time']
#     # with open(f"result/{symbol}.csv", "a") as file:
#     #     writer = csv.writer(file)
#     #     writer.writerow([symbol, price, what, time])
#     # client = Client(Config.binance_key, Config.binance_secret_key)
#     return f'symdol: {symbol}, price:{price}, what: {what}'


def buy_or_sell(what, symbol, interval):
    time = datetime.now()

    spot = Spot()
    price = float(spot.ticker_price(symbol)['price'])
    all_bots = TradingviewBot.objects.filter(what=what, symbol=symbol, interval=interval).all()

    if not len(all_bots):
        bot = TradingviewBot(
            symbol=symbol,
            price=price,
            what=what,
            interval=interval,
            time=time
        )
        bot.save()
        return
    # print(all_bots.last().time, 'last_time')
    last_signal = all_bots.last()

    old_price = float(last_signal.price)
    ten_minus = old_price - old_price * 0.02
    ten_plus = old_price * 0.02 + old_price

    if last_signal.what == what and ten_plus <= price >= ten_minus:
        bot = TradingviewBot(
            symbol=symbol,
            price=price,
            what=what,
            interval=interval,
            time=time
        )
        bot.save()
        return
    elif last_signal.what != what:

        bot = TradingviewBot(
            symbol=symbol,
            price=price,
            what=what,
            interval=interval,
            time=time
        )
        bot.save()
        return

# def price_websocket

@shared_task()
def main():
    print('Start!')
    symbols = ["BINANCE:XRPUSDT", "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:CRVUSDT", "BINANCE:BNBUSDT", "BINANCE:ADAUSDT", "BINANCE:SOLUSDT", "BINANCE:DOTUSDT", "BINANCE:LTCUSDT", "BINANCE:AVAXUSDT"]
    intervals = [Interval.INTERVAL_1_MINUTE, Interval.INTERVAL_15_MINUTES, Interval.INTERVAL_30_MINUTES, Interval.INTERVAL_1_HOUR]

    while True:

        for interval in intervals:

            analyses = get_multiple_analysis(screener="crypto", interval=interval, symbols=symbols) # Transport endpoint is not connected

            for analysis in analyses:
                symbol = analyses[analysis].symbol
                summary = analyses[analysis].summary
                print(f'symbol: {symbol}, summary: {summary}, time: {datetime.now()}')
                if summary['RECOMMENDATION'] == 'STRONG_SELL' or summary['RECOMMENDATION'] == 'STRONG_BUY':
                    buy_or_sell(summary['RECOMMENDATION'], symbol, interval)
        sleep(5)



@shared_task()
def dept_socket_manager():
    async def main_as():
        client = await AsyncClient.create()
        bm = BinanceSocketManager(client)
        # start any sockets here, i.e a trade socket
        # ts = bm.trade_socket('BNBBTC')
        ts = bm.depth_socket('ETHUSDT')
        # then start receiving messages
        async with ts as tscm:
            while True:
                res = await tscm.recv()
                cache.set("qwerty", json.dumps(res), timeout=None)
                print(len(res['b']))
                # print(res['b'])
                # print(res)

        await client.close_connection()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_as())


@shared_task()
def set_depth_cache():
    # client = await AsyncClient.create(tld='us')
    # bm = BinanceSocketManager(client)

    symbol = 'BNBBTC'
    # twm = ThreadedWebsocketManager()
    # twm.start()

    # depth cache manager using threads
    dcm = ThreadedDepthCacheManager()
    dcm.start()

    def handle_socket_message(msg):
        print(f"message type: {msg['e']}")
        print(msg)

    def handle_dcm_message(depth_cache):
        bids = depth_cache.get_bids()
        # print(len(bids))
        asks = depth_cache.get_asks()
        # only_qty = [bid[1] for bid in bids]
        # only_qty.sort(reverse=True)
        cache.set('qwerty', json.dumps({"a": asks, "b": bids}))

        # print(only_qty)

        # print(dir(depth_cache))
        # print(len(depth_cache.get_asks()))
        # print(depth_cache.get_asks().sort(reverse=True))

        # if depth_cache.get_asks()[:5][1][1] > 19:
        #     ...
        print(f"symbol {depth_cache.symbol}")
        # print("top 5 bids")
        # print(depth_cache.get_bids())
        # print("top 5 asks")
        # print(depth_cache.get_asks())
        # print("last update time {}".format(depth_cache.update_time))

    # There is no current event loop in thread
    asyncio.set_event_loop(asyncio.new_event_loop())

    dcm.start_depth_cache(callback=handle_dcm_message, symbol='ETHUSDT')

    # twm.join()
    dcm.join()
