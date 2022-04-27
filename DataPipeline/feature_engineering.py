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

import sys
sys.path.append('/home/mourad/DS/pers/kaggle/')

from MyTradingPlatform.DataPipeline.data_acquisition import get_historical_data


def resample(df, time_period = '1d'):
	# print(df.head(5))

	df1 = df[['Open']].resample(time_period).first()
	df2 = df[['Close']].resample(time_period).last()
	df3 = df[['Volume']].resample(time_period).sum()
	df = pd.concat([df1,df2,df3], axis = 0).sort_index().groupby('OpenTime').sum()
	return df

def add_cols(df):

	
	#Logging the data is very common in financial data do to it's proclivity for outliers and skewness.
	#logging the opening and closing prices helps us make the historical prices more normally distributed. 
	df['log_open'] = np.log(df['Open'])
	df['log_close'] = np.log(df['Close'])

	#Logging the return and shifting allows us to normalize the returns, this also makes the returns additive
	#rather than multiplicative.
	df['return'] = np.log(df['Close']/df['Close'].shift(1)).shift(1)
	
	#Knowing the close of the asset price over the last 7 days can be beneficial in predicting the price of
	#the next day
	for i in range(7):
		days_ago = f'close_{i+1}_prior'
		df[days_ago] = df['log_close'].shift(i+1)
	
	#The simple moving average of the closing price of the asset helps smooth the data. It can help determine
	#whether the price will continue moving in a certain diretion or change course. 
	df['sma_7'] = df['Close'].rolling(7).mean().shift(1)
	df['sma_30'] = df['Close'].rolling(30).mean().shift(1)
	df['sma_50'] = df['Close'].rolling(50).mean().shift(1)
	df['sma_200'] = df['Close'].rolling(200).mean().shift(1)

	#The distance between the closing price and the simple moving average can help identify possible reversals
	#in price direction. Crossovers can prove valuable in determining the sentiment of the asset.
	df['dist_sma_7'] = (df['Close'] - df['sma_7']).shift(1)
	df['dist_sma_30'] = (df['Close'] - df['sma_30']).shift(1)
	df['dist_sma_50'] = (df['Close'] - df['sma_50']).shift(1)
	df['dist_sma_200'] = (df['Close'] - df['sma_200']).shift(1)

	#Momentum is a measure that shows how strong an asset is moving in a particular direction. Stronger values
	#mean the current trend is likely to continue.
	df['momentum_7'] = df['return'].rolling(7).mean().shift(1)
	df['momentum_30'] = df['return'].rolling(30).mean().shift(1)
	df['momentum_50'] = df['return'].rolling(50).mean().shift(1)
	df['momentum_200'] = df['return'].rolling(200).mean().shift(1)
	
	#This shows the degress at which prives move. Asssets that are highly volatile are riskier (such as crypto-
	#currencies).
	df['volatility_7'] = df['return'].rolling(7).std().shift(1)
	df['volatility_30'] = df['return'].rolling(7).std().shift(1)
	df['volatility_50'] =  df['return'].rolling(50).std().shift(1)
	df['volatility_200'] = df['return'].rolling(200).std().shift(1)
	
	#The volume of trades can confirm the momentum of the stock or alert for the possibility of a reversal.
	df['volume_7'] = df['Volume'].rolling(7).mean().shift(1)
	df['volume_14'] = df['Volume'].rolling(14).mean().shift(1)
	df['volume_30'] = df['Volume'].rolling(30).mean().shift(1)
	df['volume_50'] = df['Volume'].rolling(50).mean().shift(1)
	
	df['Volume'] = df['Volume'].shift(1)

	df.dropna(inplace = True)
	
	return df

# btc = get_historical_data(interval='1h', first_ts = 'January 1 2019')

# daily = add_cols(resample(btc, time_period='1h'))

# print(daily.shape)
# print(daily.head(5))

