from binance.exceptions import BinanceAPIException
from django.contrib.auth import get_user_model
from django.shortcuts import get_list_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, get_object_or_404, ListAPIView, \
    ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import api_view

from apps.user.models import UserAPIKeysModel
from apps.user.serializers import UserSerializer, APIKeysSerializer

from binance.client import Client

UserModel = get_user_model()


class User(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        pk = self.request.user.id
        user = get_object_or_404(UserModel, pk=pk)

        return user


class UserCreate(CreateAPIView):
    permission_classes = [AllowAny]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer


class ListUsers(ListAPIView):
    permission_classes = [IsAdminUser]
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer


class AddOrGetAPIKeys(ListCreateAPIView):
    queryset = UserAPIKeysModel.objects.all()
    serializer_class = APIKeysSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        secret_key = self.request.data.get('secret_key')
        api_key = self.request.data.get('api_key')
        testnet = self.request.data.get('testnet')
        market = self.request.data.get('market')

        try:
            client = Client(api_key, secret_key, testnet=testnet)

            if market == 'Spot':
                client.get_account()
            else:
                client.futures_account_balance()

        except BinanceAPIException as error:
            raise ValidationError(error.message)

        serializer.save()

    def get_queryset(self):
        user = self.request.user
        list_user_keys = get_list_or_404(UserAPIKeysModel, user=user)
        return list_user_keys


class DeleteAPIKeys(DestroyAPIView):
    queryset = UserAPIKeysModel.objects.all()
    serializer_class = APIKeysSerializer
    permission_classes = [IsAuthenticated]


@api_view(['GET'])
def get_user_orders(request):
    user_id = request.user.id
    crypto_keys = UserAPIKeysModel.objects.filter(user=user_id)
    result = []
    for user_api_keys in crypto_keys:
        try:
            client = Client(user_api_keys.api_key, user_api_keys.secret_key)
            client.get_all_orders(symbol='BTCUSDT')
        except BinanceAPIException:
            return Response(f'invalid API-key {user_api_keys.name}', status=status.HTTP_400_BAD_REQUEST)
    print(crypto_keys)
    return Response('hello huy', status=status.HTTP_200_OK)
