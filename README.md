funny-bot-bitcoin
=================

Funny Bot for Mtgox Bitcoin Auto Transaction

* You take Full responsibility for Your money and bitcoin.
* You should understand what are you doing when you use funny-bot-bitcoin.

How to use
=================
    First: Set Yourself Mtgox Key and Secrect in main.py

    Then: Run command below:

    python main.py bot max_btc max_usd init_action init_price trigger_percent

    demo:

    python main.py bot 2 200 sell 93.73 0.03

    * max_btc: max amount of btc to sell
    * max_usd: max amount of usd to buy btc
    * init_action: action when start, 'sell' or 'buy'
    * init_price: price that trigger init_action
    * trigger_percent: price change percent to trigger bot action(sell or buy)

Utility
=================

    list wallets:
    python main.py wallets

    list orders:
    python main.py orders

    cancel all orders:
    python main.py cancel_all

    current ticker:
    python main.py ticker

    buy btc:
    python main.py buy 1.1 100.10    #buy 1.1 btc price: $100.10

    sell btc:
    python main.py sell 1.1 100.10    #sell.1 btc price: $100.10

    
Donate
=================
bitcoin address: 14DTHftDBvb1XSigevSYYNGmQ9iA182xor


