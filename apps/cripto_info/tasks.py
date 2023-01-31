import asyncio
import csv
import json
from datetime import datetime
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_django.settings")

import django

django.setup()

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
from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager

from tradingview_ta import get_multiple_analysis, Interval, TA_Handler

from apps.cripto_info.models import Bots
from config import Config


# TODO idea for bot on future when rsi from 70 to < 70 SHORT, when rsi from 30 to > 30 LONG


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
        # ETHUSDT 30 minute, volume 2922.8883, ten_volume = volume * 0.005 = 14.6144415, len_ask = 17
        symbol = 'BTCUSDT'
        btc_depths = self.spot.depth(symbol, )
        # print([ask[1] for ask in btc_depths['asks'] if float(ask[1]) >= 10])

        volume = float(self.spot.klines(symbol, '30m')[-1][5])
        print(f'volume for 30 minute: {volume}')
        print(len(btc_depths['asks']))
        ten_volume = volume * 0.005  # todo try ml formuly, ask vitaliy
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
    list_symbols = [item['symbol'] for item in exchange_info if "USDT" in item['symbol']]

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


######################################################## BOT Tradingview get_multiple_analysis #######################################################
class BotTradingview:

    def __init__(self):
        self.client = Client(Config.binance_key, Config.binance_secret_key)
        self.spot = Spot()
        self.um_futures = UMFutures()

    def buy_or_sell(self, what, symbol, interval):

        time = datetime.now()

        try:
            price = float(json.loads(cache.get('prices'))[symbol])
        except:
            price = float(self.spot.ticker_price(symbol=symbol)['price'])
            print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!! {symbol} !!!!!!!!!!!!!!')
            print(price)

        all_bots = Bots.objects.filter(what=what, symbol=symbol, interval=interval).all()

        if not len(all_bots):
            bot = Bots(
                bot='tradingview',
                symbol=symbol,
                price=price,
                what=what,
                interval=interval,
                time=time
            )
            bot.save()
            return

        last_signal = all_bots.last()

        old_price = float(last_signal.price)
        ten_minus = old_price - old_price * 0.02
        ten_plus = old_price * 0.02 + old_price
        # 0.0002 for price in 20 000 $ ten_plus = old_price * 0.0002 + old_price == 20 004
        # 0.0003 for price in 0.3786 $ ten_plus = old_price * 0.0003 + old_price == 0.37871358
        # may be what need timeframe not price

        if last_signal.what == what and ten_plus <= price >= ten_minus:
            bot = Bots(
                bot='tradingview',
                symbol=symbol,
                price=price,
                what=what,
                interval=interval,
                time=time
            )
            bot.save()
            return
        elif last_signal.what != what:

            bot = Bots(
                bot='tradingview',
                symbol=symbol,
                price=price,
                what=what,
                interval=interval,
                time=time
            )
            bot.save()
            return

    # def price_websocket
    # postgres://dev:7lNuhyQoXZI8mdUSsHPZTjn44XBS5oBs@dpg-ceus3iha6gdjl6qdcpig-a.frankfurt-postgres.render.com/cryptoanalysis_84pw

    def main(self):
        print('Start BOT TRADINGVIEW!')
        symbols = ["BINANCE:XRPUSDT", "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:CRVUSDT", "BINANCE:BNBUSDT",
                   "BINANCE:BNBBUSD", "BINANCE:ADAUSDT", "BINANCE:SOLUSDT", "BINANCE:DOTUSDT", "BINANCE:LTCUSDT",
                   "BINANCE:AVAXUSDT"]
        intervals = [Interval.INTERVAL_1_MINUTE, Interval.INTERVAL_15_MINUTES, Interval.INTERVAL_30_MINUTES,
                     Interval.INTERVAL_1_HOUR]

        # set_price.delay([symbol.split(':')[1] for symbol in symbols])

        while True:

            for interval in intervals:
                # https://scanner.tradingview.com/
                analyses = get_multiple_analysis(screener="crypto", interval=interval,
                                                 symbols=symbols)  # Transport endpoint is not connected

                for analysis in analyses:
                    symbol = analyses[analysis].symbol
                    summary = analyses[analysis].summary
                    if summary['RECOMMENDATION'] == 'STRONG_SELL' or summary['RECOMMENDATION'] == 'STRONG_BUY':
                        # print(f'symbol: {symbol}, summary: {summary}, time: {datetime.now()}')
                        self.buy_or_sell(summary['RECOMMENDATION'], symbol, interval)
            sleep(5)


@shared_task()
def check_ten():
    symbols = ["BINANCE:XRPUSDT", "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT"]
    intervals = [Interval.INTERVAL_1_MINUTE, Interval.INTERVAL_15_MINUTES, Interval.INTERVAL_30_MINUTES,
                 Interval.INTERVAL_1_HOUR]

    dict_data = {
        "XRPUSDT": [],
        "BTCUSDT": [],
        "ETHUSDT": [],
        "BNBUSDT": [],
        # "CRVUSDT": [],
    }

    # set_price.delay([symbol.split(':')[1] for symbol in symbols])

    # for interval in intervals:
    #     for symbol in symbols:
    #         with open(f"result/{symbol}-{interval}.csv", "r") as file:
    #             reader = list(csv.DictReader(file))
    #             result = []
    #             for data in reader:
    #                 if '2023-01-16 ' in data['time']:
    #
    #                     if not result:
    #                         result.append(data)
    #                     elif result[-1]['event'] == data['event']:
    #                         result.append(data)
    #                     elif result[-1]['event'] != data['event']:
    #                         dict_data[symbol].append(result)
    #                         result = [data]
    #
    #
    #             dict_data[symbol].append(result)

    ############################ перший buy sell ###############################
    # for interval in intervals:
    #     for symbol in symbols:
    #         with open(f"result/{symbol}-{interval}.csv", "r") as file:
    #             reader = list(csv.DictReader(file))
    #             result = []
    #             for data in reader:
    #                 if '2023-01-16 ' in data['time']:
    #                     if not result:
    #                         result.append(data)
    #                     elif data['event'] != result[-1]['event']:
    #                         result.append(data)
    #                 else:
    #                     ...
    #                     # print(data['time'])
    #             dict_data[symbol].append(result)

    # for symbol in dict_data:
    #     for data in dict_data[symbol]:
    #         list_price = [{"price": d['price'], "interval": d['interval'], "event": d["event"]} for d in data]
    #         if list_price:
    #             max_price = max([d["price"] for d in list_price])
    #             min_price = min([d["price"] for d in list_price])
    #             print(f'symbol: {symbol}, interval: {list_price[0]["interval"]}, event: {list_price[0]["event"]}, min_price: {min_price}, max_price: {max_price}')

    while True:
        for interval in intervals:
            analyses = get_multiple_analysis(screener="crypto", interval=interval, symbols=symbols)
            for analysis in analyses:
                summary = analyses[analysis].summary
                symbol = analyses[analysis].symbol
                time = analyses[analysis].time
                if summary['RECOMMENDATION'] == 'STRONG_SELL' or summary['RECOMMENDATION'] == 'STRONG_BUY':
                    # print(cache.get('prices'))
                    # print('111111111111111111111111111111')

                    try:
                        price = json.loads(cache.get('prices'))[symbol]
                    except:
                        spot = Spot()
                        price = spot.ticker_price(symbol=symbol)['price']
                        print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!! {symbol} !!!!!!!!!!!!!!')
                        print(price)
                    # if price:
                    #     price = json.loads(price)
                    #     if symbol not in price:
                    #         set_price.delay(symbol)
                    #         print(cache.get('prices'))
                    #         sleep(3)
                    #         print(cache.get('prices'))
                    #         price = json.loads(cache.get('prices'))[symbol]
                    #     else:
                    #         price = price[symbol]
                    # else:
                    #     set_price.delay(symbol)
                    #     print(json.loads(cache.get('prices')))
                    #     sleep(3)
                    #     print(json.loads(cache.get('prices')))
                    #     price = json.loads(cache.get('prices'))[symbol]

                    # price = float(spot.ticker_price(symbol)['price'])
                    with open(f"result/{symbol}-{interval}.csv", "a", newline='') as file:
                        writer = csv.writer(file)
                        # writer.writerow(['symbol', "price", 'event', 'interval', 'time'])
                        writer.writerow([symbol, price, summary['RECOMMENDATION'], interval, time])
                        file.close()
        sleep(5)


def check_with_balance():
    usdt_balance = 100
    xrp_balance = 0
    ten_balance = 100 * 0.1
    orders = []
    symbols = ["XRPUSDT"]  # , "BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT"]
    intervals = [
        Interval.INTERVAL_1_MINUTE]  # , Interval.INTERVAL_15_MINUTES, Interval.INTERVAL_30_MINUTES, Interval.INTERVAL_1_HOUR]
    for symbol in symbols:
        for interval in intervals:
            with open(f"result/{symbol}-{interval}.csv", "r") as file:
                dict_data = csv.DictReader(file)
                for data in dict_data:
                    if orders:
                        last_order = orders[-1]
                        if last_order['event'] != data['event']:
                            orders.append(data)
                    elif not orders and data['event'] == "STRONG_BUY":
                        orders.append(data)

    for order in orders:
        price = order['price']
        event = order['event']

        if event == 'STRONG_BUY':
            xrp_balance += ten_balance / price
            usdt_balance -= ten_balance
        else:
            usdt_balance += xrp_balance * price
            xrp_balance = 0

    print(orders)


def check_with_qqe_signal():
    eth_ta = TA_Handler(interval=Interval.INTERVAL_30_MINUTES, screener='crypto', symbol="ETHUSDT", exchange='BINANCE')
    btc_ta = TA_Handler(interval=Interval.INTERVAL_30_MINUTES, screener='crypto', symbol="BTCUSDT", exchange='BINANCE')
    xrp_ta = TA_Handler(interval=Interval.INTERVAL_30_MINUTES, screener='crypto', symbol="XRPUSDT", exchange='BINANCE')
    crv_ta = TA_Handler(interval=Interval.INTERVAL_30_MINUTES, screener='crypto', symbol="CRVUSDT", exchange='BINANCE')

    over_sold = 30
    over_bought = 70

    data = [
        {"symbol": 'ETHUSDT', "handler": eth_ta},
        {"symbol": 'BTCUSDT', "handler": btc_ta},
        {"symbol": 'XRPUSDT', "handler": xrp_ta},
        {"symbol": 'CRVUSDT', "handler": crv_ta},
    ]

    while True:
        result = []

        for item in data:
            rsi = item['handler'].get_indicators()['RSI']

            chop = rsi > 40 and rsi < 60  # red
            chop_tight = rsi > 45 and rsi < 55  # red
            trend_oversold = rsi < over_sold  # green
            trend_overbought = rsi > over_bought  # green
            # trend_buy = crossover(rsi, over_sold) # green
            # trend_sell = crossunder(rsi, over_bought) # green

            print(f"symbol: {item['symbol']}, rsi: {rsi}")

            if chop or chop_tight:
                print('red')
                if item in result:
                    result.remove(item)
                    print(f'green! {result}')
            elif trend_oversold or trend_overbought:
                print(f'sure green{item}')
            else:
                print('green')
                if item not in result:
                    result.append(item)
                    print(f'green!, {result}')

        sleep(10)

    # print(eth_ta.indicators)

    # analysis = get_multiple_analysis(
    #     additional_indicators='',
    #     screener="crypto",
    #     interval=Interval.INTERVAL_30_MINUTES,
    #     symbols=["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT"]
    # )
    # for a in analysis:
    #     print(analysis[a].indicators)
    #     print(dir(analysis[a]))


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

        await client.close_connection()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_as())


# @shared_task()
# def set_depth_cache():
#     # client = await AsyncClient.create(tld='us')
#     # bm = BinanceSocketManager(client)
#
#     symbol = 'ETHUSDT'
#     # twm = ThreadedWebsocketManager()
#     # twm.start()
#
#     # depth cache manager using threads
#     dcm = ThreadedDepthCacheManager()
#     dcm.start()
#
#     def handle_socket_message(msg):
#         print(f"message type: {msg['e']}")
#         print(msg)
#
#     def handle_dcm_message(depth_cache):
#         bids = depth_cache.get_bids()
#         asks = depth_cache.get_asks()
#         cache.set('qwerty', json.dumps({"a": asks, "b": bids}))
#
#         # if depth_cache.get_asks()[:5][1][1] > 19:
#         #     ...
#         print(f"symbol {depth_cache.symbol}")
#
#     # There is no current event loop in thread
#     asyncio.set_event_loop(asyncio.new_event_loop())
#
#     dcm.start_depth_cache(callback=handle_dcm_message, symbol=symbol)
#
#     # twm.join()
#     dcm.join()


##################################################### BOT Futures RSI #######################################
class BotRSI:
    def __init__(self):
        self.client = Client(Config.binance_key, Config.binance_secret_key)
        self.spot = Spot()
        self.um_futures = UMFutures()

    def long(self, symbol, interval):
        try:
            price = float(json.loads(cache.get('prices'))[symbol])
        except:
            price = float(self.spot.ticker_price(symbol=symbol)['price'])
            print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!! {symbol} !!!!!!!!!!!!!!')
            print(price)

        bot = Bots(
            bot='rsi',
            symbol=symbol,
            price=price,
            what='START_LONG',
            interval=interval,
            time=datetime.now()
        )
        bot.save()
        bot.what = f'START_LONG №{bot.id}'
        bot.save()

        start_position.delay(
            {
                "id": bot.id,
                "price": bot.price,
                "what": bot.what,
                "interval": bot.interval,
                "symbol": bot.symbol,
                "time": bot.time
            }
        )

    def short(self, symbol, interval):
        try:
            price = float(json.loads(cache.get('prices'))[symbol])
        except:
            price = float(self.spot.ticker_price(symbol=symbol)['price'])
            print(f'!!!!!!!!!!!!!!!!!!!!!!!!!!! {symbol} !!!!!!!!!!!!!!')
            print(price)

        bot = Bots(
            bot='rsi',
            symbol=symbol,
            price=price,
            what='START_SHORT',
            interval=interval,
            time=datetime.now()
        )

        bot.save()
        bot.what = f'START_SHORT №{bot.id}'
        bot.save()

        start_position.delay(
            {
                "id": bot.id,
                "price": bot.price,
                "what": bot.what,
                "interval": bot.interval,
                "symbol": bot.symbol,
                "time": bot.time
            }
        )

    def profit(self, price, symbol, interval, what):
        bot = Bots(
            bot='rsi',
            symbol=symbol,
            price=price,
            what=what,
            interval=interval,
            time=datetime.now()
        )
        bot.save()

    def change_stop_los(self, start_position):
        ...

    def in_position(self, start_position):
        symbol = start_position['symbol']
        start_price = float(start_position['price'])
        what = start_position['what']
        how_much = 0.001
        print(f'Start in_postsion: {symbol}, {what}, {start_price}')
        # print(0.003 + 0.006 + 0.009 + 0.012 + 0.015 + 0.018 + 0.021 + 0.024 + 0.027 + 0.03)
        # print(0.009 + 0.018 + 0.027 + 0.036 + 0.045 + 0.054 + 0.063 + 0.072 + 0.081 + 0.09)

        while True:
            price = float(json.loads(cache.get('prices'))[symbol])

            if how_much > 0.01:
                return
            elif 'START_LONG' in what:
                price_take_profit = start_price * how_much + start_price

                if price <= start_price - start_price * how_much and how_much == 0.001:
                    bot = Bots(
                        bot='rsi',
                        symbol=symbol,
                        price=price,
                        what=f'STOP_LOS №{start_position["id"]}',
                        interval=start_position['interva'],
                        time=datetime.now()
                    )
                    bot.save()
                    return

                if price >= price_take_profit:
                    self.profit(price, symbol, start_position['interval'], f'take_profit №{start_position["id"]}: {how_much * 3}%')
                    how_much += 0.001

            elif 'START_SHORT' in what:
                price_take_profit = start_price - start_price * how_much

                if price >= start_price * how_much + start_price and how_much == 0.001:
                    bot = Bots(
                        bot='rsi',
                        symbol=symbol,
                        price=price,
                        what=f'STOP_LOS №{start_position["id"]}',
                        interval=start_position["interval"],
                        time=datetime.now()
                    )
                    bot.save()

                    return

                elif price <= price_take_profit:
                    self.profit(price, symbol, start_position['interval'], f'take_profit №{start_position["id"]}: {how_much * 3}%')
                    how_much += 0.001

            # elif price == start_price and how_much >= 0.002:
            #     bot = Bots(
            #         bot='rsi',
            #         symbol=symbol,
            #         price=price,
            #         what='STOP_LOS',
            #         interval=start_position.interval,
            #         time=datetime.now()
            #     )
            #     bot.save()
            #
            #     return

    def bot_rsi(self):
        print('START BOT RSI!')
        interval = Interval.INTERVAL_1_MINUTE

        eth_ta = TA_Handler(interval=interval, screener='crypto', symbol="ETHUSDT", exchange='BINANCE')
        btc_ta = TA_Handler(interval=interval, screener='crypto', symbol="BTCUSDT", exchange='BINANCE')
        xrp_ta = TA_Handler(interval=interval, screener='crypto', symbol="XRPUSDT", exchange='BINANCE')
        crv_ta = TA_Handler(interval=interval, screener='crypto', symbol="CRVUSDT", exchange='BINANCE')

        data = {
            'ETHUSDT': {"handler": eth_ta, "old_rsi": None, "in_position": False},
            'BTCUSDT': {"handler": btc_ta, "old_rsi": None, "in_position": False},
            'XRPUSDT': {"handler": xrp_ta, "old_rsi": None, "in_position": False},
            'CRVUSDT': {"handler": crv_ta, "old_rsi": None, "in_position": False},
        }

        while True:
            for symbol in data:
                m = data[symbol]
                rsi = m['handler'].get_indicators()['RSI']
                if m['old_rsi']:

                    if m['old_rsi'] < 30 < rsi:
                        # sleep(2)
                        # rsi = m['handler'].get_indicators()['RSI']
                        # if rsi > 30:
                        self.long(symbol, interval)
                        m.update({"in_position": True})
                    elif m['old_rsi'] > 70 > rsi:
                        # sleep(2)
                        # rsi = m['handler'].get_indicators()['RSI']
                        # if rsi < 70:
                        self.short(symbol, interval)
                        m.update({"in_position": True})

                m.update({"old_rsi": rsi})
            sleep(5)

@shared_task()
def set_price(symbols):
    def process_new_receives(stream_data, stream_buffer_name=False):

        data = json.loads(stream_data)
        if 'data' in data:
            data = data['data']
            prices = cache.get('prices')
            if prices:
                prices = json.loads(prices)
                prices.update({data['s']: data['p']})
            else:
                prices = {data['s']: data['p']}

            cache.set('prices', json.dumps(prices))

    ubwa = BinanceWebSocketApiManager(exchange="binance.com")
    ubwa.create_stream('trade', symbols, process_stream_data=process_new_receives)


def run_all_bots():
    symbols = ["XRPUSDT", "BTCUSDT", "ETHUSDT", "CRVUSDT", "BNBUSDT", "BNBBUSD", "ADAUSDT", "SOLUSDT", "DOTUSDT", "LTCUSDT", "AVAXUSDT"]
    set_price.delay(symbols)
    run_tradingview.delay()
    run_rsi.delay()


@shared_task()
def run_tradingview():
    BotTradingview().main()


@shared_task()
def run_rsi():
    BotRSI().bot_rsi()


@shared_task()
def start_position(bot):
    BotRSI().in_position(bot)


# def test_bot_rsi():
#     print('START TEST BOT RSI!')
#     in_position()
#     interval = Interval.INTERVAL_1_MINUTE
#
#     eth_ta = TA_Handler(interval=interval, screener='crypto', symbol="ETHUSDT", exchange='BINANCE')
#     xrp_ta = TA_Handler(interval=interval, screener='crypto', symbol="XRPUSDT", exchange='BINANCE')
#     crv_ta = TA_Handler(interval=interval, screener='crypto', symbol="CRVUSDT", exchange='BINANCE')
#     btc_ta = TA_Handler(interval=interval, screener='crypto', symbol="BTCUSDT", exchange='BINANCE')
#
#     data = {
#         'ETHUSDT': {"handler": eth_ta, "old_rsi": 29, "in_position": False},
#         'BTCUSDT': {"handler": btc_ta, "old_rsi": 30.1, "in_position": False},
#         'XRPUSDT': {"handler": xrp_ta, "old_rsi": 49, "in_position": False},
#         'CRVUSDT': {"handler": crv_ta, "old_rsi": 71, "in_position": False},
#     }
#
#     for symbol in data:
#         m = data[symbol]
#         rsi = 69.9
#         if m['old_rsi']:
#
#             if m['old_rsi'] < 30 < rsi:
#                 # print(f'LONG {symbol}')
#
#                 # test_long(symbol, interval)
#                 m.update({"in_position": True})
#             elif m['old_rsi'] > 70 > rsi:
#                 # print(f'SHORT {symbol}')
#                 # test_short(symbol, interval)
#                 m.update({"in_position": True})
#
#         m.update({"old_rsi": rsi})
#
#
# def in_position():
#     symbol = 'CRVUSDT'
#     start_price = 1.34
#     what = 'START_SHORT'
#     how_much = 0.003
#
#     price = 1.36
#
#     if how_much > 0.03:
#         return
#     elif what == 'START_LONG':
#         print('START_LONG')
#         price_take_profit = start_price * how_much + start_price
#         # print('start_price - start_price * how_much', start_price - start_price * how_much)
#         # print('price', price)
#         # print('price <= start_price - start_price * how_much', price <= start_price - start_price * how_much)
#
#         if price <= start_price - start_price * how_much and how_much == 0.003:
#             print(F'STOP_LOS, start_price: {start_price} stop_price {start_price - start_price * how_much}')
#             # bot = Bots(
#             #     bot='rsi',
#             #     symbol=symbol,
#             #     price=price,
#             #     what='STOP_LOS',
#             #     interval=start_position.interval,
#             #     time=datetime.now()
#             # )
#             # bot.save()
#             return
#
#         if price >= price_take_profit:
#             print(f'take_profit, price: {price}, price_take_profit: {price_take_profit}')
#             # self.profit(price, symbol, start_position.interval, f'take_profit: {how_much * 3}%')
#             how_much += 0.003
#
#     elif what == 'START_SHORT':
#         print('START_SHORT')
#         price_take_profit = start_price - start_price * how_much
#
#         if price >= start_price * how_much + start_price and how_much == 0.003:
#             print(F'STOP_LOS, start_price: {start_price} stop_price {start_price * how_much + start_price}')
#
#             # bot = Bots(
#             #     bot='rsi',
#             #     symbol=symbol,
#             #     price=price,
#             #     what='STOP_LOS',
#             #     interval=start_position.interval,
#             #     time=datetime.now()
#             # )
#             # bot.save()
#
#             return
#
#         elif price <= price_take_profit:
#             print(f'take_profit, price: {price}, price_take_profit: {price_take_profit}')
#             # self.profit(price, symbol, start_position.interval, f'take_profit: {how_much * 3}%')
#             how_much += 0.003
#
#     # elif price == start_price and how_much != 0.003:
#         # bot = Bots(
#         #     bot='rsi',
#         #     symbol=symbol,
#         #     price=price,
#         #     what='STOP_LOS',
#         #     interval=start_position.interval,
#         #     time=datetime.now()
#         # )
#         # bot.save()
#
#         # return
#

class RillBotRSI:
    # todo коли ми знаходимося в позиції шорт і rsi < 30 тоді ми закриваємо позицію
    def __init__(self, symbol, interval, exchange):
        self.client = Client(Config.binance_key, Config.binance_secret_key)
        self.spot = Spot()
        self.um_futures = UMFutures()
        self.symbol = symbol
        self.interval = interval
        self.exchange = exchange

    def bot_rsi(self):
        print('START BOT RSI!')
        interval = self.interval

        handler = TA_Handler(interval=interval, screener='crypto', symbol=self.symbol, exchange=self.exchange)

        old_rsi = None

        while True:

            rsi = handler.get_indicators()['RSI']
            if old_rsi:

                if old_rsi < 30 < rsi:
                        ...
                        # self.long(symbol, interval)
                        # m.update({"in_position": True})
                elif old_rsi > 70 > rsi:
                        ...
                        # self.short(symbol, interval)
                        # m.update({"in_position": True})

            old_rsi = rsi
            sleep(5)
