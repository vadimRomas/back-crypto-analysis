from django.db import models

# Create your models here.


# class GraphModel(models.Model):
#     class Meta:
#         db_table = "graph"
#
#     open_time = models.DateTimeField()
#     open = models.FloatField()
    # "High",\
    # "Low",\
    # "Close",\
    # "Volume",\
    # "Close_time",\
    # "Quote_asset_volume",
    # "Number_of_trades",
    # "Taker_buy_base_asset_volume",
    # "Taker_buy_quote_asset_volume",
    # "Ignore"

class TradingviewBot(models.Model):

    class Meta:
        db_table = "tradingview_bot"

    symbol = models.CharField(max_length=20)
    price = models.FloatField()
    what = models.CharField(max_length=50)
    interval = models.CharField(max_length=10)
    time = models.DateTimeField(blank=False)
