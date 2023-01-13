from django.urls import path

from apps.cripto_info.views import GraphRetrieveAPIView, graphs, all_symbols, get_price, get_all_orders, \
    search_big_gamer, room, get_tradingview_bot, get_depth

urlpatterns = [
    path("graph", GraphRetrieveAPIView.as_view()),
    path('', graphs),
    path('symbols', all_symbols),
    path('price', get_price),
    path('orders', get_all_orders),
    path('kit', search_big_gamer) ,# maybe whale
    path('tradingview_bot', get_tradingview_bot),
    path('depth', get_depth)
    # path("<str:room_name>/", room, name="room"),
    # path('save/img/s3', lambda_save_graf)
]
