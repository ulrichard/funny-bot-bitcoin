'''
https://github.com/perol/funny-bot-bitcoin
'''

import time, hmac, base64, hashlib, urllib, urllib2, json, sys, datetime, random

key = '232fd807-607d-47f7-8a15-93e32683293b'
secret = '9UmQT2PJ2feMa7b8hCD2ttDLKWjiAdsv4GbGmtv4LSV8s8a9FhmkutE+YMefNs0tz9LSiezIJgnYwshkQJWxfw=='

import traceback, cStringIO
def get_err():
    f = cStringIO.StringIO( )
    traceback.print_exc(file=f)
    return f.getvalue( )

class mtgox:
    timeout = 15
    tryout = 8

    def __init__(self, key='', secret='', agent='btc_bot'):
        self.key, self.secret, self.agent = key, secret, agent
        self.time = {'init': time.time(), 'req': time.time()}
        self.reqs = {'max': 10, 'window': 10, 'curr': 0}
        self.base = 'https://mtgox.com/api/2/'

    def throttle(self):
        # check that in a given time window (10 seconds),
        # no more than a maximum number of requests (10)
        # have been sent, otherwise sleep for a bit
        diff = time.time() - self.time['req']
        if diff > self.reqs['window']:
            self.reqs['curr'] = 0
            self.time['req'] = time.time()
        self.reqs['curr'] += 1
        if self.reqs['curr'] > self.reqs['max']:
            print 'Request limit reached...'
            time.sleep(self.reqs['window'] - diff)

    def makereq(self, path, data):
        # bare-bones hmac rest sign
        return urllib2.Request(self.base + path, data, {
            'User-Agent': self.agent,
            'Rest-Key': self.key,
            'Rest-Sign': base64.b64encode(str(hmac.new(base64.b64decode(self.secret), path + chr(0) + data, hashlib.sha512).digest())),
        })

    def req(self, path, inp={}):
        t0 = time.time()
        tries = 0
        while True:
            # check if have been making too many requests
            self.throttle()

            try:
                # send request to mtgox
                inp['nonce'] = str(int(time.time() * 1e6))
                inpstr = urllib.urlencode(inp.items())
                req = self.makereq(path, inpstr)
                response = urllib2.urlopen(req, inpstr)

                # interpret json response
                output = json.load(response)
                if 'error' in output:
                    raise ValueError(output['error'])
                return output
                
            except Exception as e:
                print "Error: %s" % e, e.read()

            # don't wait too long
            tries += 1
            if time.time() - t0 > self.timeout or tries > self.tryout:
                raise Exception('Timeout')

gox = mtgox(key, secret, 'funny-bot-bitcoin')
rbtc = 100000000
rusd = 100000

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
    return gox.req('BTCUSD/money/order/cancel', {'oid': order_id})

def cancel_all():
    res  = []
    for order in get_orders():
        res.append(gox.req('BTCUSD/money/order/cancel', {'oid': order['oid']}))
    return res

def get_order_result(ctype, order_id):
    #only for complete order
    #ctype: bid or ask
    return gox.req('BTCUSD/money/order/result', {'type': ctype, 'order': order_id})

def lag():
    return gox.req('BTCUSD/money/order/lag')

def quote(ctype, amount):
    return gox.req('BTCUSD/money/order/quote', {'amount': amount, 'type': ctype}) 

def now():
    return datetime.datetime.now()

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
        current_price = int(ticker2()['last']['value_int'])
        print now(), 'run_once', my_btc, my_usd, current_price, self.next_action, self.next_price
        if self.next_action=='sell':
            amount = min(self.max_btc, my_btc)
            if current_price>=self.next_price or random.random()<=0.01:
                sell(amount)
                self.next_action = 'buy'
                self.next_price = int(current_price*(1-self.trigger_percent))
                print now(), 'sell ', amount
        elif self.next_action=='buy' or random.random()>=0.99:
            money = min(self.max_usd, my_usd)
            amount = int(money*1.0/current_price)*rbtc
            if current_price<=self.next_price:
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
            time.sleep(3*60)

        
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



