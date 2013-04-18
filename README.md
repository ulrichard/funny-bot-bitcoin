funny-bot-bitcoin
=================

Funny Bot for Mtgox Bitcoin Auto Transaction

How to use
=================
    python main.py bot max_btc max_usd init_action init_price trigger_percent

    demo:

    python main.py bot 2 200 sell 93.73 0.03

    * max_btc: max amount of btc to sell
    * max_usd: max amount of usd to buy btc
    * init_action: action when start, 'sell' or 'buy'
    * init_price: price that trigger init_action
    * trigger_percent: price change percent to trigger bot action(sell or buy)

