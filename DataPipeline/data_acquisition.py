import pandas as pd
import numpy as np
import json
import time
from datetime import datetime, date
import pickle
import random
# import psycopg2
import os
import binance
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager



def get_historical_data(interval = '1m', symbol= 'BTCUSDT', first_ts = None, binance_api_key = None, binance_api_secret = None):
	"""
	The rest of the pipeline won't work if we don't have at least 200 days in the data. 
	
	valid intervals - 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M.

	"""
	start_time = datetime.now()
	#Create client
	if binance_api_key == None:
		binance_api_key = os.environ['binance_api_key']
		binance_api_secret = os.environ['binance_api_secret']
	client = Client(binance_api_key, binance_api_secret)

	#Convert date into int if necessary
	if isinstance(first_ts, str):
		first_ts = binance.helpers.date_to_milliseconds(first_ts) 

	#Get the most data possible if nothing specified
	if first_ts == None:
		first_ts = client._get_earliest_valid_timestamp(symbol, interval)


	bars = client.get_historical_klines(symbol, interval, first_ts, limit=1000)

	#Converting into dataframe
	df = pd.DataFrame(data = bars, \
					  columns=['OpenTime', 'Open', 'High','Low', 'Close', 'Volume', 'CloseTime',\
									   'QuoteAssetVolume', 'NumberOfTrades', 'TakerBuyBaseAssetVolume', \
									   'TakeBuyQuoteAssetVolume', 'Ignore' ])

	#Converting columns in different type.
	df['OpenTime'] = df['OpenTime'].apply(lambda x : datetime.fromtimestamp(x//1000))
	col_float = ['Open','High', 'Low', 'Close', 'Volume', 'CloseTime','QuoteAssetVolume', 'NumberOfTrades', \
				 'TakerBuyBaseAssetVolume','TakeBuyQuoteAssetVolume', 'Ignore']
	for c in col_float:
		df[c] = df[c].astype(float)

	df= df.sort_values('OpenTime')
	df = df.set_index('OpenTime')


	print(len(bars), 'klines were acquired.')
	print('Query time:', datetime.now() - start_time)

	return df


def get_list_symbols(binance_api_key = None, binance_api_secret = None):
	client = Client(binance_api_key, binance_api_secret)
	exchangeInfo = client.get_exchange_info()

	exchangeSymbols = []
	for i in exchangeInfo['symbols']:
		exchangeSymbols.append(i)
	coins_df = pd.DataFrame(exchangeSymbols)
	return coins_df.symbol.to_list()


def get_list_coins(binance_api_key = None, binance_api_secret = None):
	client = Client(binance_api_key, binance_api_secret)
	exchangeInfo = client.get_exchange_info()

	exchangeSymbols = []
	for i in exchangeInfo['symbols']:
		exchangeSymbols.append(i)
	coins_df = pd.DataFrame(exchangeSymbols)
	return list(set(coins_df.baseAsset.to_list()))
