import os

def set_binance_key(value):
	env_var = 'binance_api_key'
	os.environ[env_var] = value

def set_binance_secret(value):
	env_var = 'binance_api_secret'
	os.environ[env_var] = value


def get_binance_key():
	val = os.getenv('binance_api_key') 
	if not val:
		return 'Not found'
	return val 

def get_binance_secret():

	val = os.getenv('binance_api_secret') 
	if not val:
		return 'Not found'
	return val 


