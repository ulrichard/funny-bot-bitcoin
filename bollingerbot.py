from func import *
import random
import pandas as pd
import numpy as np

class BollingerBot(object):
    def __init__(self, interval, lookback):
		print now(), 'init_bot', interval, lookback
		self.interval = interval
		self.lookback = lookback

		self.prices = []
		self.prices.append(np.zeros((1, 2)));
		self.prices.append(np.zeros((1, 2)));

		self.prices = pd.DataFrame(self.prices, index=[], columns=['ask', 'bid'])

    def run_once(self):
		wallets = get_wallets()
		my_usd = int(wallets['USD']['Balance']['value_int'])
		my_btc = int(wallets['BTC']['Balance']['value_int'])

		curr_ask = current_ask_price()
		curr_bid = current_bid_price()
		self.prices.append(pd.DataFrame([curr_ask, curr_bid], columns=['ask', 'bid']))
		if pd.rolling_count(self.prices['ask']) < self.lookback:
			print 'only ', pd.rolling_count(self.prices['ask']), ' observations so far'
			return

		means = pd.rolling_mean(self.prices, self.lookback, min_periods = self.lookback)
		stddev = pd.rolling_std(self.prices, self.lookback, min_periods = self.lookback)
		lower = means - stddev
		upper = means + stddev
		normalized = (close - means) / stddev

		timestamps = self.prices.index

		# should we sell? 
		bollinger_ask_now  = normalized['ask'].ix[ldt_timestamps[len(timestamps) - 1]]
		bollinger_ask_last = normalized['ask'].ix[ldt_timestamps[len(timestamps) - 2]]
		if bollinger_ask_now <= -2.0 and bollinger_ask_last >= -2.0:
			print now(), 'begin sell ', my_btc
			print 'sell result', sell(my_btc)

		# should we buy? 
		bollinger_bid_now  = normalized['bid'].ix[ldt_timestamps[len(timestamps) - 1]]
		bollinger_bid_last = normalized['bid'].ix[ldt_timestamps[len(timestamps) - 2]]
		if bollinger_bid_now >= 2.0 and bollinger_bid_last <= 2.0:
			amount = int(my_usd / curr_bid)
			print now(), 'begin buy ', amount
			print 'sell result', buy(amount)


    def run(self):
        while 1:
            try:
                self.run_once()
            except:
                print now(), "Error - ", get_err()
            time.sleep(60 * self.interval)

