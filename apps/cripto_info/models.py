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

class Bots(models.Model): #TradingviewBot

    class Meta:
        db_table = "bots"

    symbol = models.CharField(max_length=20)
    bot = models.CharField(max_length=50, null=True)
    price = models.FloatField()
    what = models.CharField(max_length=50)
    interval = models.CharField(max_length=10)
    time = models.DateTimeField(blank=False)


# class RSIBot(models.Model):
#     class Meta:
#         db_table = "rsi_bot"
#
#     symbol = models.CharField(max_length=20)
#     price = models.FloatField()
#     what = models.CharField(max_length=50) # STOP_LOS, TAKE_PROFIT, START_POSITION
#     interval = models.CharField(max_length=10)
#     time = models.DateTimeField(blank=False)


# XRPUSDT,0.3856,STRONG_SELL,1m,2023-01-16 09:42:12.862875
# XRPUSDT,0.3879,STRONG_BUY,1m,2023-01-16 10:33:11.204634
# XRPUSDT,0.3861,STRONG_SELL,1m,2023-01-16 10:47:41.658445
# XRPUSDT,0.3859,STRONG_BUY,1m,2023-01-16 12:17:14.487591
# XRPUSDT,0.3854,STRONG_SELL,1m,2023-01-16 12:24:40.606890
# XRPUSDT,0.3867,STRONG_BUY,1m,2023-01-16 13:11:12.500254
# XRPUSDT,0.3856,STRONG_SELL,1m,2023-01-16 13:37:41.684315
# XRPUSDT,0.3858,STRONG_BUY,1m,2023-01-16 14:21:18.489334
# XRPUSDT,0.3851,STRONG_SELL,1m,2023-01-16 14:39:51.830437

# XRPUSDT,0.3853,STRONG_SELL,15m,2023-01-16 09:57:42.444446


# ETHUSDT,1550.91,STRONG_BUY,1m,2023-01-16 10:14:44.515787
# ETHUSDT,1545.75,STRONG_SELL,1m,2023-01-16 10:54:42.868775


# BTCUSDT,20786.59,STRONG_SELL,1m,2023-01-16 09:43:45.952252

# BTCUSDT,20805.23,STRONG_SELL,15m,2023-01-16 11:30:12.617948


# BNBUSDT,298.9,STRONG_SELL,1m,2023-01-16 10:18:45.174551
# BNBUSDT,300.8,STRONG_BUY,1m,2023-01-16 12:03:11.439068
# BNBUSDT,298.8,STRONG_SELL,1m,2023-01-16 12:13:49.181139

# BNBUSDT,298.5,STRONG_SELL,15m,2023-01-16 09:46:41.314856
