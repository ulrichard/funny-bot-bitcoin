funny-bot-bitcoin
=================

![funny bot bitcoin](/funny-bot-bitcoin.png "BOT")

Funny Bot for Mtgox Bitcoin Auto Transaction

* funny-bot-bitcoin is very fresh and it's strategy is VERY idiotic, 
* funny-bot-bitcoin should just your starting point
* You take Full responsibility for Your money and bitcoin.
* You should understand what are you doing when you use funny-bot-bitcoin.

How to use
=================
    First: Set Yourself Mtgox Key and Secrect in mtgox_key.py

    Then: Run command below:

    python main.py bot max_btc max_usd init_action init_price trigger_percent

    demo:

    python main.py bot 2 200 sell 93.73 0.03

    * max_btc: max amount of btc to sell every time
    * max_usd: max amount of USD($) to buy btc every time
    * init_action: action when start, 'sell' or 'buy'
    * init_price: price that trigger init_action
    * trigger_percent: price change percent to trigger bot action(sell or buy)

How funny-bot-bitcoin work
=================

    init_action(sell/buy).... Sell ==> Buy ==> Sell ==> Buy ==> Sell ==> Buy==> Sell ==> Buy

    Every 2 minutes, funny-bot-bitcoin watch the newest price, 
    when it higher/lower than the init_price, trigger init_action(sell/buy)

    After init_action, sell/buy alternately begin the current action

    When the newest price higher/lower than  previous_price*(1 -/+ trigger_percent), 
    then trigger the current action(sell/buy)

    OR 1/100 Probability trigger the current action whatever the newest price is.



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

    buy btc at the market price:
    python main.py buy 1.1     #buy 1.1 btc at the market price

    sell btc:
    python main.py sell 1.1 100.10    #sell.1 btc price: $100.10

    sell btc at the market price:
    python main.py sell 1.1    #sell.1 btc at the market price
    
Donate
=================
Bitcoin Address: 14DTHftDBvb1XSigevSYYNGmQ9iA182xor


