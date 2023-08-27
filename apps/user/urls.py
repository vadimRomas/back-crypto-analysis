from django.urls import path

from apps.user.views import User, UserCreate, AddOrGetAPIKeys, DeleteAPIKeys, get_user_orders, UserBotsCreateView, \
    UserBotsUpdateView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register', UserCreate.as_view()),
    path('', User.as_view()),
    path('login', TokenObtainPairView.as_view(), name='tokens'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
    path('cryptoapikeys', AddOrGetAPIKeys.as_view()),
    path('cryptoapikeys/<int:pk>', DeleteAPIKeys.as_view()),
    path('orders', get_user_orders),
    path('bot', UserBotsCreateView.as_view()),
    path('bot/<int:pk>', UserBotsUpdateView.as_view())
]
