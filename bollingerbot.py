from func import *
import random

class BollingerBot(object):
    def __init__(self, max_btc, max_usd, init_action, init_price, trigger_percent):
        print now(), 'init_bot', max_btc, max_usd, init_action, init_price, trigger_percent
        self.max_btc = max_btc
        self.max_usd = max_usd
        self.trigger_percent = trigger_percent
        self.next_action = init_action
        self.next_price = init_price

    def run_once(self):
        wallets = get_wallets()
        my_usd = int(wallets['USD']['Balance']['value_int'])
        my_btc = int(wallets['BTC']['Balance']['value_int'])
        if self.next_action=='sell':
            current_price = current_ask_price()
            print now(), 'run_once', my_btc, my_usd, current_price, self.next_action, self.next_price
            amount = min(self.max_btc, my_btc)
            if current_price>=self.next_price or random.random()<=0.01:
                print now(), 'begin sell ', amount
                print 'sell result', sell(amount)
                self.next_action = 'buy'
                self.next_price = int(current_price*(1-self.trigger_percent))
                print now(), 'sell ', amount
        elif self.next_action=='buy':
            current_price = current_bid_price()
            print now(), 'run_once', my_btc, my_usd, current_price, self.next_action, self.next_price
            money = min(self.max_usd, my_usd)
            amount = int(money*1.0/current_price*rbtc)
            if current_price<=self.next_price or random.random()>=0.99:
                print now(), 'begin buy', amount
                print 'buy result', buy(amount)
                self.next_action = 'sell'
                self.next_price = int(current_price*(1+self.trigger_percent))
                print now(), 'buy', amount

    def run(self):
        while 1:
            try:
                self.run_once()
                #time.sleep(60)
                #print 'cancel all orders:', cancel_all()
            except:
                print now(), "Error - ", get_err()
            time.sleep(120)

