from binance.streams import ThreadedWebsocketManager
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient


class OrderBook:
    ...


import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

api_key = '9wdt1hUkbaqX8V5wi6QKkWn2JHQv7ux6ydScV1g22tbARcYyQplEBNl339IB1WPd'
api_secret = 'HSawkzk7tca8uJYA6UkDqsomWWODOEiUcgmHlV0LIaaBSRUHodXQVzD7EdQMXJ1W'
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
