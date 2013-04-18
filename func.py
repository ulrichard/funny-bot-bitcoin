import urllib2, json, datetime 
from mtgox import mtgox
from mtgox_key import key, secret

gox = mtgox(key, secret, 'funny-bot-bitcoin')
rbtc = 100000000
rusd = 100000

import traceback, cStringIO
def get_err():
    f = cStringIO.StringIO( )
    traceback.print_exc(file=f)
    return f.getvalue( )
        
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

