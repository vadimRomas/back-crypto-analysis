# import asyncio
#
# from binance.client import AsyncClient
# from binance.streams import BinanceSocketManager
# from celery import shared_task
# from django.core.cache import cache
#
#
# @shared_task()
# def set_price(symbol):
#     async def main():
#         client = await AsyncClient.create()
#         bm = BinanceSocketManager(client)
#         # start any sockets here, i.e a trade socket
#         ts = bm.trade_socket(symbol.upper())
#         async with ts as tscm:
#             while True:
#                 res = await tscm.recv()
#                 prices = cache.get('prices')
#                 if prices:
#                     prices = json.loads(prices)
#                     prices.update({symbol: res['p']})
#                 else:
#                     prices = {res['s']: res['p']}
#
#                 cache.set('prices', prices)
#
#         await client.close_connection()
#
#     loop = asyncio.get_event_loop()
#     loop.run_until_complete(main())
# import numpy as np
# import pandas as pd
# import yfinance as yf
# import pandas_datareader.data as web
# import pandas_ta as ta
# import matplotlib.pyplot as plt
# from datetime import date
#
# plt.style.use('fivethirtyeight')
# yf.pdr_override()
#
# stocksymbols = ['TATAMOTORS.NS'] #  nice!!!!!!!!!!!!!!!!!!!!!!!!!
# startdate = date(2021,8,4)
# end_date = date.today()
# print(end_date)
# def getMyPortfolio(stocks = stocksymbols ,start = startdate , end = end_date):
#     data = web.get_data_yahoo(stocks , start = start ,end= end )
#     return data
#
# data = getMyPortfolio(stocksymbols)
# print(data)
# data['SMA 30'] = ta.sma(data['Close'],30)
# data['SMA 100'] = ta.sma(data['Close'],100)
# #SMA BUY SELL
# #Function for buy and sell signal
# def buy_sell(data):
#     signalBuy = []
#     signalSell = []
#     position = False
#
#     for i in range(len(data)):
#         if data['SMA 30'][i] > data['SMA 100'][i]:
#             if position == False :
#                 signalBuy.append(data['Adj Close'][i])
#                 signalSell.append(np.nan)
#                 position = True
#             else:
#                 signalBuy.append(np.nan)
#                 signalSell.append(np.nan)
#         elif data['SMA 30'][i] < data['SMA 100'][i]:
#             if position == True:
#                 signalBuy.append(np.nan)
#                 signalSell.append(data['Adj Close'][i])
#                 position = False
#             else:
#                 signalBuy.append(np.nan)
#                 signalSell.append(np.nan)
#         else:
#             signalBuy.append(np.nan)
#             signalSell.append(np.nan)
#     return pd.Series([signalBuy, signalSell])
#
# data['Buy_Signal_price'], data['Sell_Signal_price'] = buy_sell(data)
#
#
# fig, ax = plt.subplots(figsize=(14,8))
# ax.plot(data['Adj Close'] , label = stocksymbols[0] ,linewidth=0.5, color='blue', alpha = 0.9)
# ax.plot(data['SMA 30'], label = 'SMA30', alpha = 0.85)
# ax.plot(data['SMA 100'], label = 'SMA100' , alpha = 0.85)
# ax.scatter(data.index , data['Buy_Signal_price'] , label = 'Buy' , marker = '^', color = 'green',alpha =1 )
# ax.scatter(data.index , data['Sell_Signal_price'] , label = 'Sell' , marker = 'v', color = 'red',alpha =1 )
# ax.set_title(stocksymbols[0] + " Price History with buy and sell signals",fontsize=10, backgroundcolor='blue', color='white')
# ax.set_xlabel(f'{startdate} - {end_date}' ,fontsize=18)
# ax.set_ylabel('Close Price INR (₨)' , fontsize=18)
# legend = ax.legend()
# ax.grid()
# plt.tight_layout()
# plt.show()
#
#
# macd = ta.macd(data['Close'])
#
#
# data = pd.concat([data, macd], axis=1).reindex(data.index)
#
# def MACD_Strategy(df, risk):
#     MACD_Buy=[]
#     MACD_Sell=[]
#     position=False
#
#     for i in range(0, len(df)):
#         if df['MACD_12_26_9'][i] > df['MACDs_12_26_9'][i] :
#             MACD_Sell.append(np.nan)
#             if position == False:
#                 MACD_Buy.append(df['Adj Close'][i])
#                 position=True
#             else:
#                 MACD_Buy.append(np.nan)
#         elif df['MACD_12_26_9'][i] < df['MACDs_12_26_9'][i] :
#             MACD_Buy.append(np.nan)
#             if position == True:
#                 MACD_Sell.append(df['Adj Close'][i])
#                 position=False
#             else:
#                 MACD_Sell.append(np.nan)
#         elif position == True and df['Adj Close'][i] < MACD_Buy[-1] * (1 - risk):
#             MACD_Sell.append(df["Adj Close"][i])
#             MACD_Buy.append(np.nan)
#             position = False
#         elif position == True and df['Adj Close'][i] < df['Adj Close'][i - 1] * (1 - risk):
#             MACD_Sell.append(df["Adj Close"][i])
#             MACD_Buy.append(np.nan)
#             position = False
#         else:
#             MACD_Buy.append(np.nan)
#             MACD_Sell.append(np.nan)
#
#     data['MACD_Buy_Signal_price'] = MACD_Buy
#     data['MACD_Sell_Signal_price'] = MACD_Sell
#
#
# MACD_strategy = MACD_Strategy(data, 0.025)
#
# def MACD_color(d):
#     color = []
#     for i in range(0, len(d)):
#         if d['MACDh_12_26_9'][i] > d['MACDh_12_26_9'][i - 1]:
#             color.append(True)
#         else:
#             color.append(False)
#     return color
#
# data['positive'] = MACD_color(data)
#
#
# plt.rcParams.update({'font.size': 10})
# fig, ax1 = plt.subplots(figsize=(14,8))
# fig.suptitle(stocksymbols[0], fontsize=10, backgroundcolor='blue', color='white')
# import json
# ax1 = plt.subplot2grid((14, 8), (0, 0), rowspan=8, colspan=14)
# ax2 = plt.subplot2grid((14, 12), (10, 0), rowspan=6, colspan=14)
# ax1.set_ylabel('Price in ₨')
# ax1.plot('Adj Close',data=data, label='Close Price', linewidth=0.5, color='blue')
# # print(data)
# ax1.scatter(data.index, data['MACD_Buy_Signal_price'], color='green', marker='^', alpha=1)
# ax1.scatter(data.index, data['MACD_Sell_Signal_price'], color='red', marker='v', alpha=1)
# ax1.legend()
# ax1.grid()
# ax1.set_xlabel('Date', fontsize=8)
#
# ax2.set_ylabel('MACD', fontsize=8)
# ax2.plot('MACD_12_26_9', data=data, label='MACD', linewidth=0.5, color='blue')
# ax2.plot('MACDs_12_26_9', data=data, label='signal', linewidth=0.5, color='red')
# ax2.bar(data.index,'MACDh_12_26_9', data=data, label='Volume', color=data.positive.map({True: 'g', False: 'r'}),width=1,alpha=0.8)
# ax2.axhline(0, color='black', linewidth=0.5, alpha=0.5)
# ax2.grid()
# plt.show()
#
#
# def bb_strategy(data):
#     bbBuy = []
#     bbSell = []
#     position = False
#     bb = ta.bbands(data['Adj Close'], length=20,std=2)
#     data = pd.concat([data, bb], axis=1).reindex(data.index)
#
#     for i in range(len(data)):
#         if data['Adj Close'][i] < data['BBL_20_2.0'][i]:
#             if position == False :
#                 bbBuy.append(data['Adj Close'][i])
#                 bbSell.append(np.nan)
#                 position = True
#             else:
#                 bbBuy.append(np.nan)
#                 bbSell.append(np.nan)
#         elif data['Adj Close'][i] > data['BBU_20_2.0'][i]:
#             if position == True:
#                 bbBuy.append(np.nan)
#                 bbSell.append(data['Adj Close'][i])
#                 position = False #To indicate that I actually went there
#             else:
#                 bbBuy.append(np.nan)
#                 bbSell.append(np.nan)
#         else :
#             bbBuy.append(np.nan)
#             bbSell.append(np.nan)
#
#     data['bb_Buy_Signal_price'] = bbBuy
#     data['bb_Sell_Signal_price'] = bbSell
#
#     return data
#
# #storing the function
# data = bb_strategy(data)
#
# #plot
# fig, ax1 = plt.subplots(figsize=(14,8))
# fig.suptitle(stocksymbols[0], fontsize=10, backgroundcolor='blue', color='white')
# ax1 = plt.subplot2grid((14, 8), (0, 0), rowspan=8, colspan=14)
# ax2 = plt.subplot2grid((14, 12), (10, 0), rowspan=6, colspan=14)
# ax1.set_ylabel('Price in ₨')
# ax1.plot(data['Adj Close'],label='Close Price', linewidth=0.5, color='blue')
# ax1.scatter(data.index, data['bb_Buy_Signal_price'], color='green', marker='^', alpha=1)
# ax1.scatter(data.index, data['bb_Sell_Signal_price'], color='red', marker='v', alpha=1)
# ax1.legend()
# ax1.grid()
# ax1.set_xlabel('Date', fontsize=8)
#
# ax2.plot(data['BBM_20_2.0'], label='Middle', color='blue', alpha=0.35) #middle band
# ax2.plot(data['BBU_20_2.0'], label='Upper', color='green', alpha=0.35) #Upper band
# ax2.plot(data['BBL_20_2.0'], label='Lower', color='red', alpha=0.35) #lower band
# ax2.fill_between(data.index, data['BBL_20_2.0'], data['BBU_20_2.0'], alpha=0.1)
# ax2.legend(loc='upper left')
# ax2.grid()
# plt.show()
#




# import websocket
# import json
# import numpy as np
# import talib
# candles = []
# def on_message(ws, message):
#     message = json.loads(message)
#     print(message['k']['c'])
#     candles.append(float(message['k']['c']))
#     close = np.array(candles, dtype=float)
#     rsi = talib.RSI(close, timeperiod=14)
#     print("RSI:", rsi[-1])
#
# def on_error(ws, error):
#     print("error:", error)
#
# def on_close(ws):
#     print("Closed connection")
#
# def on_open(ws):
#     print("Opened connection")
#
# websocket.enableTrace(True)
# ws = websocket.WebSocketApp("wss://fstream.binance.com/ws/btcusdt@kline_1m",
#                               on_message=on_message,
#                               on_error=on_error,
#                               on_close=on_close)
# ws.on_open = on_open
# ws.run_forever()

# import requests
# import csv
# import time
#
# def get_historical_price(symbol, interval):
#     url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit=1000"
#     response = requests.get(url)
#     data = response.json()
#     return [[int(candle[0]/1000), float(candle[1]), float(candle[2]), float(candle[3]), float(candle[4]), float(candle[5])] for candle in data]
#
# def save_to_csv(data, file_name):
#     with open(file_name, 'w') as file:
#         writer = csv.writer(file)
#         writer.writerow(['timestamp', 'open', 'high', 'low', 'close', 'volume'])
#         for row in data:
#             writer.writerow(row)
#
# symbol = "BTCUSDT"
# interval = "1m"
# candles = get_historical_price(symbol, interval)
# save_to_csv(candles, "bitcoin_price.csv")


# import pandas as pd
# import numpy as np
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
#
# # Load the dataset
# df = pd.read_csv('bitcoin_price.csv')
#
# # Clean the dataset
# df = df.dropna()
#
# # Prepare the data for modeling
# X = df[['open', 'high', 'low', 'close', 'volume']]
# y = df['close']
#
# # Split the data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
#
# # Scale the data
# scaler = StandardScaler()
# X_train = scaler.fit_transform(X_train)
# X_test = scaler.transform(X_test)
#
# # Train the model
# model = RandomForestRegressor(n_estimators=100, random_state=0)
# model.fit(X_train, y_train)
#
# # Predict the future price
# future_price = model.predict(X_test)
# print(future_price)
# [23036.8224 23259.3497 23676.2677 23676.173  23636.4467 23121.9514
#  23744.8408 23783.52   23672.9718 23646.6872 23733.1372 23686.7024
#  23307.81   23716.2821 23721.3962 23706.5966 23245.6077 23861.5254
#  23803.0965 23788.6348 23737.1034 23751.3695 23673.0292 23680.9139
#  23257.0646 23287.1868 23685.3661 23783.1511 23539.3202 23785.2403
#  23142.0738 23662.7567 23701.9465 23273.921  23629.1691 23586.7167
#  23115.9072 23630.7553 23206.6756 23758.1824 23792.5158 23067.6995
#  23693.9637 23647.7076 23701.4107 23319.0384 23191.9174 23771.2858
#  23663.4405 23719.256  23664.2559 23674.4354 23731.6381 23648.7768
#  23259.4939 23733.9526 23768.4355 23762.3518 23050.1856 23644.5333
#  23710.9017 23698.1597 23773.6161 23754.0117 23654.8063 23773.8077
#  23748.0415 23707.4153 23722.9393 23721.3404 23588.288  23663.6794
#  23580.6522 23705.392  23153.1233 23653.0956 23621.0539 23295.3827
#  23715.7928 23667.7885 23739.6077 23697.3222 23614.5579 23009.5851
#  23253.8106 23641.6025 23765.8092 23733.263  23726.45   23222.41
#  23679.8772 23742.9672 23139.6828 23752.1046 23700.1423 23736.3657
#  23707.6035 23794.3684 23637.0005 23702.5022 23260.5488 23220.8065
#  23724.6574 23228.2044 23655.012  23697.6942 23637.3298 23291.0369
#  23125.004  23782.3586 23799.5103 23733.7045 23720.1596 23711.9418
#  23741.5988 23621.0876 23688.6814 23614.6575 23746.9907 23704.2917
#  23343.6928 23231.4545 23789.428  23139.6271 23717.8039 23290.7345
#  23637.7891 23762.3166 23081.2232 23723.2449 23731.7655 23690.4409
#  23730.4084 23664.0257 23562.4227 23682.4064 23674.5045 23812.5154
#  23694.0198 23221.7685 23795.0043 23702.4807 23705.9421 23708.2696
#  23761.7166 23660.4764 23622.713  23632.1173 23720.4341 23687.3473
#  23771.3621 23736.4297 23630.1761 23547.982  23084.1523 23049.6591
#  23700.6348 23614.3459 23271.0811 23741.1573 23730.1562 23047.6839
#  23630.7977 23259.2712 23166.051  23608.2233 23659.4005 23107.3096
#  23604.2109 23667.5465 23134.5561 23292.5788 23764.4878 23206.405
#  23749.8869 23561.6559 23731.456  23693.9722 23257.4991 23768.123
#  23391.2537 23073.4099 23720.5552 23650.8517 23061.5632 23114.9146
#  23662.9886 23698.9314 23358.0135 23748.1097 23254.8814 23231.7943
#  23654.0795 23797.0294 23345.7945 23651.9191 23620.09   23765.95
#  23673.2373 23759.6906]
