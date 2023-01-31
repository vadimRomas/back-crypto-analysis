import telebot
from binance.spot import Spot

from config import Config
import asyncio

from binance.client import AsyncClient
from binance.streams import BinanceSocketManager


async def main(chat_id, price, symbol, what):
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)
    ts = bm.trade_socket(symbol.upper())

    async with ts as tscm:
        while True:
            res = await tscm.recv()
            print(res)
            if what == '>' and float(res['p']) > price:
                telegram.send_message(chat_id, f'symbol: {symbol}, price: {res["p"]}')
                return
            elif what == '<' and float(res['p']) < price:
                telegram.send_message(chat_id, f'symbol: {symbol}, price: {res["p"]}')
                return


    await client.close_connection()


telegram = telebot.TeleBot(Config.telegram_token)


@telegram.message_handler(commands=['start', 'help'])
def start_telegram(msg):
    telegram.reply_to(msg, "Привіт я бот ****! Чим може вам допомогти?")


# @telegram.message_handler(func=lambda msg: True)
def echo_all(chat, message):
    if '>' in message and '<' in message:
        list_word = message.split()

        if len(list_word) == 1:
            list_word = message.split('>')

        symbol = list_word[0]
        price_one = list_word
        price_two = list_word

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(
            main(
                chat_id=chat,
                symbol=symbol,
                what='<>',
                price=[price_one, price_two]
            )
        )
    elif '>' in message:
        list_word = message.split()

        if len(list_word) == 1:
            list_word = message.split('>')

        symbol = list_word[0]
        what = '>'
        price = float(list_word[-1])

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(
            main(
                chat_id=chat,
                symbol=symbol,
                what=what,
                price=price
            )
        )
    elif '<' in message:
        list_word = message.split()

        if len(list_word) == 1:
            list_word = message.split('<')

        symbol = list_word[0]
        what = '<'
        price = float(list_word[-1])

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(
            main(
                chat_id=chat,
                symbol=symbol,
                what=what,
                price=price
            )
        )

    else:
        telegram.reply_to(message, 'ладно я але ти, ТИ!')


@telegram.message_handler(commands=['notification'], content_types=["text"])
def notification_price_crypto_coin(message):
    echo_all(message.chat.id, message.text.split('/notification')[-1])
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    #
    # loop.run_until_complete(main(message.chat.id))
    # telegram.send_message(message, 'fuck you')


@telegram.message_handler(commands=['fuck'])
def hvala(message):
    telegram.send_message(message.chat.id, 'ох і файний той програміст який мене пише')


@telegram.message_handler(commands=['price'])
def price_coin(message):
    spot = Spot()
    symbol = message.text.split()[-1].upper()
    print(symbol)
    price = spot.ticker_price(symbol)['price']
    telegram.send_message(message.chat.id, price)


telegram.infinity_polling()
