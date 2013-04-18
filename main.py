'''
https://github.com/perol/funny-bot-bitcoin
'''

import time, hmac, base64, hashlib, urllib, urllib2, json, sys, datetime, random

key = 'your key'
secret = 'your secret'

import traceback, cStringIO
def get_err():
    f = cStringIO.StringIO( )
    traceback.print_exc(file=f)
    return f.getvalue( )

from mtgox import mtgox
gox = mtgox(key, secret, 'funny-bot-bitcoin')
rbtc = 100000000
rusd = 100000

def now():
    return datetime.datetime.utcnow()

def ticker():
    return json.loads(urllib2.urlopen('http://data.mtgox.com/api/1/BTCUSD/ticker').read())['return']

def ticker2():
    return json.loads(urllib2.urlopen('http://data.mtgox.com/api/2/BTCUSD/money/ticker').read())['data']

def get_wallets():
    info = gox.req('money/info', {})
    return info['data']['Wallets']

def get_orders():
    return gox.req('money/orders')['data']

def buy(amount, price=None):
    if price is None:
        return gox.req('BTCUSD/money/order/add', {'amount_int': amount, 'type': 'bid'})
    else:
        return gox.req('BTCUSD/money/order/add', {'amount_int': amount, 'type': 'bid', 'price_int': price})

def sell(amount, price=None):
    if price is None:
        return gox.req('BTCUSD/money/order/add', {'amount_int': amount, 'type': 'ask'})
    else:
        return gox.req('BTCUSD/money/order/add', {'amount_int':amount, 'type': 'ask', 'price_int': price})

def cancel(order_id):
    return gox.req('money/order/cancel', {'oid': order_id})

def cancel_all():
    res  = []
    for order in get_orders():
        res.append(cancel(order['oid']))
    return res

def get_order_result(ctype, order_id):
    #only for complete order
    #ctype: bid or ask
    return gox.req('money/order/result', {'type': ctype, 'order': order_id})

def lag():
    return gox.req('money/order/lag')

def quote(ctype, amount):
    return gox.req('BTCUSD/money/order/quote', {'amount': amount, 'type': ctype}) 

def current_bid_price():
    return quote('bid', rbtc)['data']['amount']

def current_ask_price():
    return quote('ask', rbtc)['data']['amount']

class Bot(object):
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
                sell(amount)
                self.next_action = 'buy'
                self.next_price = int(current_price*(1-self.trigger_percent))
                print now(), 'sell ', amount
        elif self.next_action=='buy' or random.random()>=0.99:
            current_price = current_bid_price()
            print now(), 'run_once', my_btc, my_usd, current_price, self.next_action, self.next_price
            money = min(self.max_usd, my_usd)
            amount = int(money*1.0/current_price)*rbtc
            if current_price<=self.next_price:
                print now(), 'begin buy', amount
                buy(amount)
                self.next_action = 'sell'
                self.next_price = int(current_price*(1+self.trigger_percent))
                print now(), 'buy', amount

    def run(self):
        while 1:
            try:
                self.run_once()
            except:
                print now(), "Error - ", get_err()
            time.sleep(2*60)

        
if __name__=='__main__':
    try:
        if sys.argv[1]=='wallets':
            wallets = get_wallets()
            for wallet in wallets:
                print wallet, wallets[wallet]['Balance']['display']

        elif sys.argv[1]=='orders':
            for order in get_orders():
                print order['oid'], order['status'], order['type'], 'price: ', order['price']['display'], \
                    'amount: ', order['amount']['display']

        elif sys.argv[1]=='buy':
            amount = int(float(sys.argv[2])*rbtc)
            if len(sys.argv)>=4:
                price = int(float(sys.argv[3])*rusd)
            else:
                price = None 
            print buy(amount, price)

        elif sys.argv[1]=='sell':
            amount = int(float(sys.argv[2])*rbtc)
            if len(sys.argv)>=4:
                price = int(float(sys.argv[3])*rusd)
            else:
                price = None 
            print sell(amount, price)

        elif sys.argv[1]=='cancel':
            order_id = sys.argv[2]
            print cancel(order_id)

        elif sys.argv[1]=='cancel_all':
            print cancel_all()

        elif sys.argv[1]=='result':
            ctype = sys.argv[2]    #bid or ask
            order_id = sys.argv[3]
            print get_order_result(ctype, order_id)

        elif sys.argv[1]=='ticker':
            res = ticker2()
            for k in ['last', 'high', 'low', 'avg', 'vwap', 'buy', 'sell', 'vol']:
                print k, res[k]['display_short']

        elif sys.argv[1]=='lag':
            print lag()

        elif sys.argv[1]=='quote':
            ctype = sys.argv[2]    #bid or ask
            amount = int(float(sys.argv[3])*rbtc)
            print quote(ctype, amount)

        elif sys.argv[1]=='bot':
            max_btc = int(float(sys.argv[2])*rbtc)
            max_usd = int(float(sys.argv[3])*rusd)
            init_action = sys.argv[4] #sell, buy
            init_price = int(float(sys.argv[5])*rusd)
            trigger_percent = float(sys.argv[6])
            bot = Bot(max_btc, max_usd, init_action, init_price, trigger_percent)
            bot.run()
        else:
            pass

    except Exception as e:
        print now(), "Error - ", get_err()



