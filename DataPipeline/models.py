import pandas as pd
import numpy as np
import json
import time
from datetime import datetime, date
import pickle
import random
import os
import math


import binance
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

from statsmodels.tsa.arima_model import ARMA
from statsmodels.tsa.arima.model import ARIMA, ARIMAResults
from sklearn.metrics import mean_squared_error


from MyTradingPlatform.DataPipeline.data_acquisition import get_historical_data
from MyTradingPlatform.DataPipeline.feature_engineering import resample, add_cols

def ARIMA_train(y_train, p = 0, d = 0, q = 0, train_size = None):
	"""
	y_train is a pandas series. We 
	Return in [0] the trained model, in [1] the results of the trainning. 
	"""
	train_log = y_train.apply(lambda x : math.log(x))
	train_log.index = pd.DatetimeIndex(train_log.index.values,\
									   freq=train_log.index.inferred_freq)

	aic_scores = []

	if train_size == None:
		train_size = len(y_train)

	# print('train_size', train_size)
	# print('p = ',p,', d =', d,', q = ', q)
	model = ARIMA(endog = train_log.tail(train_size), order =(p,d,q), freq = 'D')
	fitmodel = model.fit()
	rmse = np.sqrt(fitmodel.mse)
	aic_scores.append(pd.DataFrame(['ARIMA', train_size, (p,d,q), fitmodel.aic, rmse]).T)


	arima_df = pd.concat(aic_scores, axis = 0)
	arima_df.set_axis(['model type', 'train_size', 'order', 'AIC', 'RMSE'], axis = 1, inplace = True)
	return_df = arima_df.sort_values(['train_size','RMSE'], ascending = [False,True]).reset_index(drop = True)

	return fitmodel, return_df


### Predict

def ARIMA_predict(train, p = 0, d = 0, q = 0):
	"""
	Train must be a serie with date and daily values. 
	
	Return in 0 the next value with the time and in 1 the RMSE. 
	"""
	train_log = train.apply(lambda x : math.log(x))

	train_log.index = pd.DatetimeIndex(train_log.index.values,\
									   freq=train_log.index.inferred_freq)

	fitmodel, stat = ARIMA_train(train_log,  p = 3, d = 0, q = 4)

	next_step = fitmodel.forecast().apply(lambda x : math.exp(x))
	
	rmse = stat.RMSE.values[0]
	
	return next_step, rmse


### Evaluate different metrics