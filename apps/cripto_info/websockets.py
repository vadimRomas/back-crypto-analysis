import asyncio
from django.core.cache import cache

from binance.client import AsyncClient
from binance.depthcache import ThreadedDepthCacheManager
from binance.streams import ThreadedWebsocketManager, BinanceSocketManager
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from celery import shared_task


class OrderBook:
    ...


import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))





import time

from config import Config

api_key = Config.binance_key
api_secret = Config.binance_secret_key

@shared_task()
async def main_ws():

    symbol = 'BNBBTC'
    twm = ThreadedWebsocketManager()
    twm.start()

    # depth cache manager using threads
    dcm = ThreadedDepthCacheManager()
    dcm.start()

    def handle_socket_message(msg):
        print(f"message type: {msg['e']}")
        print(msg)

    def handle_dcm_message(depth_cache):
        bids = depth_cache.get_bids()
        print(len(bids))
        asks = depth_cache.get_asks()
        only_qty = [bid[1] for bid in bids]
        only_qty.sort(reverse=True)
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
    # asyncio.set_event_loop(asyncio.new_event_loop())
    # twm.start_kline_socket(callback=handle_socket_message, symbol='BNBBTC')

    dcm.start_depth_cache(callback=handle_dcm_message, symbol='ETHUSDT')
    # twm.start_depth_socket(callback=handle_socket_message, symbol='ETHUSDT')
    # streams = ["btcusdt@trade", "btcusdt@kline_1m"]
    # twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)
    # replace with a current options symbol
    # options_symbol = 'BTC-210430-36000-C'
    # dcm.start_options_depth_cache(callback=handle_dcm_message, symbol=options_symbol)

    # join the threaded managers to the main thread
    twm.join()
    dcm.join()



import time

# from binance import ThreadedWebsocketManager
# UMFuturesWebsocketClient().diff_book_depth(symbol='ethusdt', id=1, level='first', speed='speed', callback=self.callback_book_depth())
# def main():

    # symbol = 'BNBBTC'

    # twm = ThreadedWebsocketManager(api_key=api_key, api_secret=api_secret)
    # start is required to initialise its internal loop
    # twm.start()

    # def handle_socket_message(msg):
    #     print(f"message type: {msg['e']}")
    #     print(msg)

    # twm.start_kline_socket(callback=handle_socket_message, symbol=symbol)

    # multiple sockets can be started
    # print(UMFuturesWebsocketClient().diff_book_depth(symbol='ethusdt', id=1, level='first', speed='speed', callback=handle_socket_message))
    # twm.start_depth_socket(callback=handle_socket_message, symbol=symbol)

    # or a multiplex socket can be started like this
    # see Binance docs for stream names
    # streams = ['bnbbtc@miniTicker', 'bnbbtc@bookTicker']
    # twm.start_multiplex_socket(callback=handle_socket_message, streams=streams)

    # twm.join()


# if __name__ == "__main__":
#     main()
