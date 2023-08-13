from django.urls import path

from apps.cripto_info.views import graphs, all_symbols, get_price, get_all_orders, \
    search_big_gamer, get_tradingview_bot, get_depth, BotsCreateView, BotsRetrieveUpdateDestroyView, BotsListView

urlpatterns = [
    path('', graphs),
    path('symbols', all_symbols),
    path('price', get_price),
    path('orders', get_all_orders),
    path('kit', search_big_gamer) ,# maybe whale
    path('depth', get_depth),
    path('bots', BotsCreateView.as_view()),
    path('bots/list', BotsListView.as_view()),
    path('bots/RUD', BotsRetrieveUpdateDestroyView.as_view()),
]
