import csv
import json

from time import sleep
from random import randint
from asgiref.sync import async_to_sync
from binance.um_futures import UMFutures
from tradingview_ta import Interval

from apps.cripto_info.websockets import main_ws
from config import Config
from channels.generic.websocket import WebsocketConsumer

from channels.consumer import AsyncConsumer
from django.http import HttpResponse

from rest_framework.generics import ListAPIView

from apps.cripto_info.models import GraphModel

from apps.cripto_info.serializers import GraphSerializer
import pprint
from binance.client import Client
from binance.spot import Spot
from django.core.cache import cache

from apps.cripto_info.tasks import set_all, MyCache, main, set_depth_cache, buy_or_sell

spot = Spot()
client = Client(Config.binance_key, Config.binance_secret_key)


class GraphRetrieveAPIView(ListAPIView):
    queryset = GraphModel.objects.all()
    serializer_class = GraphSerializer

    def graph(self, request):
        queryset = self.get_queryset()
        pprint.pprint(queryset)
        return HttpResponse('Hello World!')


def all_symbols(request):
    # MyCache().future_depth()
    # cache.delete('symbols')
    # print('yoben~')
    # MyCache().bot_depth()
    # print('~boben')
    # main_ws()
    result = cache.get('symbols')
    if not result:
        # set_all.delay()
        main.delay()
        exchange_info = spot.ticker_price()
        result = [item['symbol'] for item in exchange_info]
        result = json.dumps(result)

    return HttpResponse(result, content_type='application/json')


def graphs(request):
    symbol = request.GET['symbol']
    time_frame = request.GET['time']

    kline = spot.klines(symbol, time_frame)
    # fild_name = ["Open_time", "Open", "High", "Low", "Close", "Volume", "Close_time", "Quote_asset_volume",
    #              "Number_of_trades", "Taker_buy_base_asset_volume", "Taker_buy_quote_asset_volume", "Ignore"]

    tak = [
        {
            "Open_time": item[0],  # datetime.fromtimestamp(item[0] / 1000),
            "Open": item[1],
            "High": item[2],
            "Low": item[3],
            "Close": item[4],
            "Volume": item[5],
            "Close_time": item[6],  # dat'-0.00003753etime.fromtimestamp(item[6] / 1000),
            "Quote_asset_volume": item[7],
            "Number_of_trades": item[8],
            "Taker_buy_base_asset_volume": item[9],
            "Taker_buy_quote_asset_volume": item[10],
            "Ignore": item[11],
        }
        for item in kline
    ]
    # with open("btc_usdt.csv", "w") as file:
    #     writer = csv.writer(file)
    #     writer.writerow(fild_name)
    #     writer.writerows(kline)

    # air_quality = pd.read_csv("btc_usdt.csv")
    # table_statics = air_quality.describe()
    # open_ = plt.plot(air_quality.Open)
    # df = pd.DataFrame(air_quality.Open)
    # print(tak[0])
    # print(klines_btc_usdt[0])
    # response = {}
    # response = HttpResponse(content_type='text/csv')
    # response['Content-Disposition'] = 'attachment; filename=btc_usdt.csv'
    #
    # air_quality.to_csv(path_or_buf=response, sep=';', float_format='%.2f', index=False, decimal=",")
    # client = Client(api_key, api_secret)
    # res = client.get_exchange_info()
    # op = client.get_symbol_info('BNBBTC')
    # # op = client.get_all_orders(symbol='BNBBTC', requests_params={'timeout': 5})
    # # return HttpResponse('Hello World!')
    # print(air_quality.Open)
    # plt.hist(air_quality.Open)
    return HttpResponse(json.dumps(tak), content_type="application/json")


def get_price(request):
    symbol = request.GET['symbol']
    # res = client.get_exchange_info()
    op = client.get_symbol_info(symbol)
    print(spot.ticker_price())

    return HttpResponse(op, content_type="application/json")


def get_alert():
    ...


def get_all_orders(request):
    symbol = request.GET['symbol']
    depths = Spot().depth(symbol=symbol)

    return HttpResponse(json.dumps(depths), 200)


def search_big_gamer(request):
    # todo change on websocket
    spot_result = cache.get("spot_depths")
    future_result = cache.get("future_depths")
    print('1111111111111111')
    # print(UMFutures().funding_rate('btcusdt'))
    # print(UMFutures().funding_rate('btcusdt'))

    long_short_account_ratio_btcusdt = UMFutures().long_short_account_ratio(period='5m', symbol='BTCUSDT')
    print(long_short_account_ratio_btcusdt[-1])
    # long_short_account_ratio = UMFutures().long_short_account_ratio(period='5m', symbol='BTCUSDT')
    long_short_account_ratio_ethusdt = UMFutures().long_short_account_ratio(period='5m', symbol='ethusdt')

    return HttpResponse(json.dumps({"spot": spot_result, "future": future_result,
                                    "long_short_account_ratio": [long_short_account_ratio_btcusdt[-1],
                                                                 long_short_account_ratio_ethusdt[-1]]}), 200)


def get_tradingview_bot(request):
    result = {"XRPUSDT": [], "BTCUSDT": [], "ETHUSDT": [], "BNBUSDT": []}
    symbols = ["XRPUSDT", "BTCUSDT", "ETHUSDT", "BNBUSDT"]
    intervals = [Interval.INTERVAL_1_MINUTE, Interval.INTERVAL_15_MINUTES, Interval.INTERVAL_30_MINUTES,
                 Interval.INTERVAL_1_HOUR]

    for symbol in symbols:
        for interval in intervals:

            try:

                with open(f'result/{symbol}-{interval}.csv', 'r') as file:
                    reader = csv.DictReader(file)

                    for row in reader:
                        result[symbol].append(row)

            except FileNotFoundError as error:
                ...

    return HttpResponse(json.dumps(result), 200)


def get_depth(request):
    # dept_socket_manager.delay()
    # set_depth_cache.delay()
    # main.delay()
    # buy_or_sell('STRONG_SELL', 'ETHUSDT', '15m')
    result = cache.get('qwerty')
    return HttpResponse(result, 200)


def websocket_big_gamer():
    # todo change on websocket
    result = cache.get("depths")

    return HttpResponse(json.dumps(result), 200)


class PracticeConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        # when websocket connects
        print("connected", event)

        await self.send({"type": "websocket.accept",
                         })

        await self.send({"type": "websocket.send",
                         "text": 0})

    async def websocket_receive(self, event):
        # when messages is received from websocket
        print("receive", event)

        sleep(1)

        await self.send({"type": "websocket.send",
                         "text": str(randint(0, 100))})

    async def websocket_disconnect(self, event):
        # when websocket disconnects
        print("disconnected", event)


class TextRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # Receive message from WebSocket
        text_data_json = json.loads(text_data)
        text = text_data_json['text']
        sender = text_data_json['sender']
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': text,
                'sender': sender
            }
        )

    def chat_message(self, event):
        # Receive message from room group
        text = event['message']
        sender = event['sender']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'text': text,
            'sender': sender
        }))


def room(request, room_name):
    # tesla = TA_Handler(
    #     symbol="TSLA",
    #     screener="america",
    #     exchange="NASDAQ",
    #     interval='30m'
    # )
    # print(tesla.get_analysis().summary)
    result = {"room_name": room_name}
    return HttpResponse(json.dumps(result), 200)

# def lambda_handler(event, context):
#     print(event)
#
#     object_get_context = event["getObjectContext"]
#     request_route = object_get_context["outputRoute"]
#     request_token = object_get_context["outputToken"]
#     s3_url = object_get_context["inputS3Url"]
#
#     # Get object from S3
#     response = requests.get(s3_url)
#     original_object = response.content.decode('utf-8')
#
#     # Transform object
#     transformed_object = original_object.upper()
#
#     # Write object back to S3 Object Lambda
#     s3 = boto3.client('s3')
#     s3.write_get_object_response(
#         Body=transformed_object,
#         RequestRoute=request_route,
#         RequestToken=request_token)
#
#     return {'status_code': 200}


# def lambda_save_graf(request):
#     symbol = request.GET['symbol']
#     time = request.GET['time']
#
#     klines_btc_usdt = spot.klines(symbol, interval=time)
#
#     tak = [
#         [
#             datetime.fromtimestamp(item[0] / 1000),
#             item[1],
#             item[2],
#             item[3],
#             item[4],
#             item[5],
#             datetime.fromtimestamp(item[6] / 1000),
#             item[7],
#             item[8],
#             item[9],
#             item[10],
#             item[11],
#         ]
#         for item in klines_btc_usdt
#     ]
#     fild_name = ["Open_time", "Open", "High", "Low", "Close", "Volume", "Close_time", "Quote_asset_volume",
#                  "Number_of_trades", "Taker_buy_base_asset_volume", "Taker_buy_quote_asset_volume", "Ignore"]
#
#     with open(f"{symbol}-{time}-{date.today()}.csv", "w") as file:
#         writer = csv.writer(file)
#         writer.writerow(fild_name)
#         writer.writerows(tak)
#
#     air_quality = pd.read_csv(f"{symbol}-{time}-{date.today()}.csv")
#     # table_statics = air_quality.describe()
#     plt.plot(air_quality.Open)
#     plt.legend()
#     plt.savefig(f'{symbol}-{time}-{date.today()}.png')
#
#     s3 = boto3.client(
#         's3',
#         aws_access_key_id='AKIA24JOEL44PE3LVWHT',
#         aws_secret_access_key='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'
#     )
#
#     s3.upload_file(f'{symbol}-{time}-{date.today()}.png', 'mycryptoanalysis', f'{symbol}-{time}-{date.today()}.png')
#     # s3.upload_file(f'{symbol}-{time}-{date.today()}.csv', 'mycryptoanalysis', f'{symbol}-{time}-{date.today()}.csv')
#
#     # list_objects = s3.list_objects(Bucket='mycryptoanalysis')
#     # size = [item['Size'] for item in list_objects["Contents"]]
#     # print(size)
#     # s3.put_object(Bucket='mycryptoanalysis', fild_name='')
#     # s3.download_file('mycryptoanalysis', f'{symbol}-{time}.png', f'download-{symbol}-{time}.png')  працює
#
#     # buckets = s3.list_buckets() work
#
#     # objects = s3.list_objects(Bucket='mycryptoanalysis') work
#
#     return HttpResponse('OK', 200)


# def lambda_symbols(event, context):
#     client = Client(api_key, api_secret)
#     exchange_info = client.get_exchange_info()
#     result = [item['symbol'] for item in exchange_info['symbols']]
#
#     return (result, 200)
#
#
# def lambda_graph(event, context):
#     symbol = event['symbol']
#     time_frame = event['time']
#
#     klines_btc_usdt = spot.klines(symbol, time_frame)
#
#     tak = [
#         {
#             "Open_time": item[0],  # datetime.fromtimestamp(item[0] / 1000),
#             "Open": item[1],
#             "High": item[2],
#             "Low": item[3],
#             "Close": item[4],
#             "Volume": item[5],
#             "Close_time": item[6],  # datetime.fromtimestamp(item[6] / 1000),
#             "Quote_asset_volume": item[7],
#             "Number_of_trades": item[8],
#             "Taker_buy_base_asset_volume": item[9],
#             "Taker_buy_quote_asset_volume": item[10],
#             "Ignore": item[11],
#         }
#         for item in klines_btc_usdt
#     ]
#
#     return HttpResponse(json.dumps(tak), content_type="application/json")
