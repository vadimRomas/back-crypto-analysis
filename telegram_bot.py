# import telebot
# from binance.spot import Spot
#
# from config import Config
# import asyncio
#
# from binance.client import AsyncClient
# from binance.streams import BinanceSocketManager
#
#
# async def main(chat_id, price, symbol, what):
#     client = await AsyncClient.create()
#     bm = BinanceSocketManager(client)
#     ts = bm.trade_socket(symbol.upper())
#
#     async with ts as tscm:
#         while True:
#             res = await tscm.recv()
#             print(res)
#             if what == '>' and float(res['p']) > price:
#                 telegram.send_message(chat_id, f'symbol: {symbol}, price: {res["p"]}')
#                 return
#             elif what == '<' and float(res['p']) < price:
#                 telegram.send_message(chat_id, f'symbol: {symbol}, price: {res["p"]}')
#                 return
#
#
#     await client.close_connection()
#
#
# telegram = telebot.TeleBot(Config.telegram_token)
#
#
# @telegram.message_handler(commands=['start', 'help'])
# def start_telegram(msg):
#     telegram.reply_to(msg, "Привіт я бот ****! Чим може вам допомогти?")
#
#
# # @telegram.message_handler(func=lambda msg: True)
# def echo_all(chat, message):
#     if '>' in message and '<' in message:
#         list_word = message.split()
#
#         if len(list_word) == 1:
#             list_word = message.split('>')
#
#         symbol = list_word[0]
#         price_one = list_word
#         price_two = list_word
#
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#
#         loop.run_until_complete(
#             main(
#                 chat_id=chat,
#                 symbol=symbol,
#                 what='<>',
#                 price=[price_one, price_two]
#             )
#         )
#     elif '>' in message:
#         list_word = message.split()
#
#         if len(list_word) == 1:
#             list_word = message.split('>')
#
#         symbol = list_word[0]
#         what = '>'
#         price = float(list_word[-1])
#
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#
#         loop.run_until_complete(
#             main(
#                 chat_id=chat,
#                 symbol=symbol,
#                 what=what,
#                 price=price
#             )
#         )
#     elif '<' in message:
#         list_word = message.split()
#
#         if len(list_word) == 1:
#             list_word = message.split('<')
#
#         symbol = list_word[0]
#         what = '<'
#         price = float(list_word[-1])
#
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#
#         loop.run_until_complete(
#             main(
#                 chat_id=chat,
#                 symbol=symbol,
#                 what=what,
#                 price=price
#             )
#         )
#
#     else:
#         telegram.reply_to(message, 'ладно я але ти, ТИ!')
#
#
# @telegram.message_handler(commands=['notification'], content_types=["text"])
# def notification_price_crypto_coin(message):
#     echo_all(message.chat.id, message.text.split('/notification')[-1])
#     # loop = asyncio.new_event_loop()
#     # asyncio.set_event_loop(loop)
#     #
#     # loop.run_until_complete(main(message.chat.id))
#     # telegram.send_message(message, 'fuck you')
#
#
# @telegram.message_handler(commands=['fuck'])
# def hvala(message):
#     telegram.send_message(message.chat.id, 'ох і файний той програміст який мене пише')
#
#
# @telegram.message_handler(commands=['price'])
# def price_coin(message):
#     spot = Spot()
#     symbol = message.text.split()[-1].upper()
#     print(symbol)
#     price = spot.ticker_price(symbol)['price']
#     telegram.send_message(message.chat.id, price)
#
#
# telegram.infinity_polling()


# from binance_f import RequestClient
# from binance_f.constant import *
# from binance_f.model import *
# from binance_f.exception.binanceapiexception import BinanceApiException
#
# api_key = '4073c840294b3c48597eeb522745c5d03e4ba0548b3b88e7c05a39356bf1f226'
# secret_key = 'c8d7ec56e6821360ee00a9468377fee371b9fe9c43af1f6f0876685a1f1b567f'
#
# # Create a request client instance
# request_client = RequestClient(api_key=api_key, secret_key=secret_key, url='https://testnet.binancefuture.com')
#
# # Place a test order
# try:
#     balances = request_client.get_balance()
#     quantity = 0
#     for balance in balances:
#         if balance.asset == 'USDT':
#             quantity = balance.balance * 0.1
#     # print(request_client.get_balance())
#     #########################################################################################3
#     order = request_client.post_order(symbol="BTCUSDT", side=OrderSide.BUY, positionSide=PositionSide.BOTH, ordertype=OrderType.MARKET, timeInForce=TimeInForce.GTC, quantity=quantity, newClientOrderId="my_order_id")
#     print(f"Test order placed. Order ID: {order.orderId}")
#     #########################################################################################3
# except BinanceApiException as e:
#     print(f"Error placing test order: {e}")


from binance.client import Client
import math

from binance.enums import KLINE_INTERVAL_1MINUTE



# Символ та кількість контрактів ф'ючерса
# symbol = "BTCUSDT"
# quantity = 1
# # print(client.futures_symbol_ticker(symbol=symbol))
#
# # Отримати баланс USDT на рахунку
# account_balance = client.futures_account_balance()
#
# usdt_balance = float([x for x in account_balance if x['asset'] == 'USDT'][0]['balance'])
#
# # Вирахувати кількість контрактів на основі 10% від балансу USDT
# quantity = (usdt_balance * 0.1) / float(client.futures_symbol_ticker(symbol=symbol)['price'])

# exchange_info = client.futures_exchange_info()
# symbol_info = next((s for s in exchange_info['symbols'] if s['symbol'] == symbol), None)
# quantity_step_size = float(symbol_info['filters'][2]['stepSize'])
# quantity = math.floor(
#     (usdt_balance * 0.1) / (float(client.futures_symbol_ticker(symbol=symbol)['price']) * quantity_step_size))
# print(quantity)

# Розмістити тестове замовлення на покупку
positions = client.futures_account()['positions']

# for position in positions:
#     if position['symbol'] == symbol:
#         print(p6osition)
#         if position['positionAmt'] == 0:
#             print('start create order')
#             order = client.futures_create_order(
#                 symbol=symbol,
#                 side=Client.SIDE_BUY,
#                 type=Client.ORDER_TYPE_MARKET,
#                 quantity=round(quantity, 3),
#                 # leverage=leverage,
#             )

# print(client.futures_get_all_orders())
# print(client.futures_get_open_orders())


# import numpy as np
#
# def calculate_rsi(prices, n=14):
#     deltas = np.diff(prices)
#     seed = deltas[:n+1]
#     up = seed[seed >= 0].sum() / n
#     down = -seed[seed < 0].sum() / n
#     rs = up / down
#     rsi = np.zeros_like(prices)
#     rsi[:n] = 100. - 100. / (1. + rs)
#
#     for i in range(n, len(prices)):
#         delta = deltas[i-1]  # cause the diff is 1 shorter
#         if delta > 0:
#             upval = delta
#             downval = 0.
#         else:
#             upval = 0.
#             downval = -delta
#         up = (up * (n - 1) + upval) / n
#         down = (down * (n - 1) + downval) / n
#         rs = up / down
#         rsi[i] = 100. - 100. / (1. + rs)
#
#     return rsi
#
#
# klines = client.futures_klines(symbol=symbol, interval=KLINE_INTERVAL_1MINUTE, limit=25)
# for kline in klines:
#     print(f'Open_time: {kline[0]}, Open: {kline[1]}, High: {kline[2]}, Low: {kline[3]}, Close: {kline[4]}, Volume: {kline[5]}, Close time: {kline[6]}, Quote asset volume: {kline[7]}, Number of trades: {kline[8]}, Taker buy base asset volume: {kline[9]}, Taker buy quote asset volume: {kline[10]}, Ignore: {kline[11]}')
# prices = [float(data[4]) for data in klines]
# # print(prices)
# # print(len([10, 12, 13, 15, 16, 18, 17, 16, 15, 14, 12, 10, 8, 9, 11, 12, 14, 15, 16, 18]))
#
# rsi = calculate_rsi(prices)
#
#
# print(rsi)
#
#
# # [
# #     1499040000000,      // Open time
# #     "0.01634790",       // Open
# #     "0.80000000",       // High
# #     "0.01575800",       // Low
# #     "0.01577100",       // Close
# #     "148976.11427815",  // Volume
# #     1499644799999,      // Close time
# #     "2434.19055334",    // Quote asset volume
# #     308,                // Number of trades
# #     "1756.87402397",    // Taker buy base asset volume
# #     "28.46694368",      // Taker buy quote asset volume
# #     "17928899.62484339" // Ignore.
# #   ]


