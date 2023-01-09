# import csv
# import os
# import time
# from importlib.util import find_spec
# from typing import Union
#
# from datetime import datetime, date
#
# import boto3
# import jwt
# import pandas as pd
# from binance.spot import Spot
# from django.core.wsgi import get_wsgi_application
# from django.http import HttpResponse
# from fastapi import FastAPI, Request
# from matplotlib import pyplot as plt
# from rest_framework.generics import CreateAPIView, DestroyAPIView
# from rest_framework.permissions import IsAuthenticated
# from starlette.middleware.wsgi import WSGIMiddleware
# from starlette.staticfiles import StaticFiles
#
# from apps.aws.models import AWSModel
# from apps.aws.serializers import AWSSerializer
#
# application = get_wsgi_application()
#
# app = FastAPI()
# # app.mount("/admin", WSGIMiddleware(application))
# app.mount("/static",
#           StaticFiles(
#               directory=os.path.normpath(
#                   os.path.join(find_spec("django.contrib.admin").origin, "..", "static")
#               )
#           ),
#           name="static",
#           )
#
#
# @app.middleware("http")
# async def add_process_time_header(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response
#
#
# @app.get("/")
# def read_root():
#     return {"Hello": "World"}
#
#
# @app.get("fastAPI/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
#
#
# class CreateAWS(CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = AWSModel.objects.all()
#     serializer_class = AWSSerializer
#
#
# class DeleteAWS(DestroyAPIView):
#     permission_classes = [IsAuthenticated]
#     queryset = AWSModel.objects.all()
#     serializer_class = AWSSerializer
#
#
# def lambda_save_graf(request):
#     symbol = request.GET['symbol']
#     time = request.GET['time']
#
#     client = Spot()
#     klines_btc_usdt = client.klines(symbol, interval=time)
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
#
#
# def activate(request):
#     jwt_token = request.headers['Authorization']
#     jwt_options = {
#         'verify_signature': True,
#         'verify_exp': True,
#         'verify_nbf': False,
#         'verify_iat': True,
#         'verify_aud': False
#     }
#     encoded_jwt = jwt.encode({
#         "token_type": "access",
#         "exp": 1678341279,
#         "iat": 1663941279,
#         "jti": "8562854decc34e098d515de321a457ff",
#         "user_id": 1
#     }, "Bearer", algorithm="HS256")
#     print(encoded_jwt)
#
#     token = jwt_token.split('Bearer ')[1]
#
#     print(token)
#
#     print(jwt.decode(encoded_jwt, "Bearer", algorithms=["HS256"]))
#     print(jwt.decode(token, 'Bearer', algorithms=['HS256'], options=jwt_options))
#
#     return HttpResponse('OK', 200)
