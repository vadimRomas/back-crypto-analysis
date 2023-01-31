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
