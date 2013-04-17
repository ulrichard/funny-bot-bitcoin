# https://bitbucket.org/nitrous/mtgox-api
# Basic MtGox API v2 implementation 
# Some code inspired by http://pastebin.com/aXQfULyq
# Don't request results more often than every 10 seconds, you risk being blocked by the anti-DDoS filters

import time,hmac,base64,hashlib,urllib,urllib2,json

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

if __name__=='__main__':
    gox = mtgox()
    try:
        bid_price = gox.req('BTCUSD/money/order/quote', {'type':'bid','amount':100000000})
        print "Current USD Bid Price: %f" % (bid_price['data']['amount'] / 1e5)
    except Exception as e:
        print "Error - %s" % e



