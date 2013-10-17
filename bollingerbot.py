#!/usr/bin/env python
# -*- coding: utf-8 -*-

from func import *
import random
import pandas as pd
import numpy as np
import urllib, json
from time import time

class BollingerBot(object):
    def __init__(self, interval, lookback):
		print now(), 'init_bot', interval, lookback
		self.interval = interval
		self.lookback = lookback

		# init data struct
		timestamps = []
		for i in range(lookback):
			timestamps.append((int(time()) / 60) - i * interval)

		all_data = np.zeros((lookback, 2))
#		for i in range(2):
#			all_data.append(np.zeros((lookback, 2)));
#			all_data[i][:][:] = np.NAN

		self.prices = pd.DataFrame(all_data, index=timestamps, columns=['ask', 'bid'])

		# read the data for the last 12 hours
		self.market = "mtgoxUSD"
		link = 'http://bitcoincharts.com/t/trades.csv?symbol=%s&start=%d&end=%d' % (self.market,
                                                                                    int(time() - 12 * 3600),
                                                                                    int(time()))
		http = urllib.urlopen(link)
		rows = http.read().split('\n')
		for row in rows:
			row = row.split(',')
			try:
				timestamp = int(row[0] / 60)
				if timestamp < (int(time()) / 60) - lookback * interval:
					continue
				value     = row[1]
				ammount   = row[2]
				self.prices[timestamp]['bid'] = max(self.prices[timestamp]['bid'], value)
				self.prices[timestamp]['ask'] = min(self.prices[timestamp]['ask'], value)
				#trades.append(tuple(map(float, row)[:2]))
			except:
				pass
		print self.prices
            

		

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

