import robin_stocks as r
import pyotp
import sys
import json
import base64
import datetime
import argparse
import orders

###################

#### PRE VARS #####

###################


# version
Version="0.0.4sp"

# TO IMPLEMENT unsync FOR FAST

run_date = datetime.datetime.now()

###################

#### FUNCTIONS ####

###################

# LOGIN
def LOGIN():
    global r
    # AUTH + LOGIN - LESS SECURE 
    # - clear text "creds" file - 3 lines: email/username , password, authkey
    # with open('creds') as f:
    #     lines = f.readlines()

    # AUTH + LOGIN - MORE SECURE
    # - more secure "creds-encoded" - we use base64 encoding (so anyone looking over your shoulder can't see your UN,PW,KEY)
    # - create by first writing cleartext "creds" file
    # - then run this in bash                       # python -c 'import base64; print(base64.b64encode(open("creds","r").read().encode("utf-8")).decode("utf-8"))' > creds-encoded
    # - confirm you see base64 alphanumerics here   # cat creds-encoded
    # - try to revert back                          # python -c 'import base64; print(base64.b64decode(open("creds-encoded","r").read()).decode("utf-8"))'
    # - if you see the email/username , password, authkey lines in that order then you can delete the "creds" file with: # rm creds
    with open("creds-encoded") as f:
        lines = base64.b64decode(f.read()).decode("utf-8").split()

    EMAIL, PASSWD, KEY = map(lambda x: x.strip(), lines)

    ptot = pyotp.TOTP(KEY)
    ptot_now = ptot.now()

    login = r.login(EMAIL,PASSWD,mfa_code=ptot_now)
    return login

###################

# GET LATEST PRICE
def QUOTE(ticker):
    ans=r.get_latest_price(ticker)
    print(f"{ticker.upper()}: ${ans[0]}")
    return ans

# BUY X SHARES OF STOCK
def BUY(ticker, amount_of_shares):
    ans=r.order_buy_market(ticker,amount_of_shares)
    print(ans)
    return ans

# SELL X SHARES OF STOCK
def SELL(ticker, amount_of_shares):
    ans=r.order_buy_market(ticker,amount_of_shares)
    print(ans)
    return ans

###################

# SIMPLE CONVERT INSTRUMENT URL TO SYMBOL
def URL2SYM(url):
    return r.get_symbol_by_url(url)

# CONVERT CURRENCY ID TO NAME
def ID2SYM(id,cryptopairs):
    for i in cryptopairs:
        if i["id"] == id:
            return i["symbol"]

###################

# CONVERT MONEY STRING TO 2 DECIMAL 
def TOMONEY(string):
    if string is None:
        return "None"
    else:
        return f"{float(string):.2f}"

###################

# FORMAT STOCKS
def FORMAT_ORDER_STOCKS(orders):
    return "\n".join([ f'{o["last_transaction_at"]} - {o["id"]} - {o["side"]}\tx{o["quantity"]}\t{URL2SYM(o["instrument"])} [S|{o["state"]}]\tavg: ${TOMONEY(o["average_price"])}\texec1/{len(o["executions"])}: ${TOMONEY(o["executions"][0]["price"])}\tprice: ${TOMONEY(o["price"])}' for o in orders ])

# FORMAT CRYPTO
def FORMAT_ORDER_CRYPTOS(orders):
    return "\n".join([ f'{o["last_transaction_at"]} - {o["id"]} - {o["side"]}\t${TOMONEY(o["rounded_executed_notional"])}\tx{o["quantity"]}\t{ID2SYM(o["currency_pair_id"],cryptopairs)} [C|{o["state"]}]\tavg: ${TOMONEY(o["average_price"])}\texec1/{len(o["executions"])}: ${TOMONEY(o["executions"][0]["effective_price"])}\tprice: ${TOMONEY(o["price"])}' for o in orders ])

# FORMAT OPTIONS
def FORMAT_ORDER_OPTIONS(orders):
    return "\n".join([ f'{o["last_transaction_at"]} - {o["id"]} - {o["side"]}\tx{o["quantity"]}\t{URL2SYM(o["instrument"])} [O|{o["state"]}]\tavg: ${TOMONEY(o["average_price"])}\texec1/{len(o["executions"])}: ${TOMONEY(o["executions"][0]["price"])}\tprice: ${TOMONEY(o["price"])}' for o in orders ])

###################

# LOAD + PRINT STOCK ORDERS OF A SYMBOL OR ALL <- old split these up below (maybe delete)
def LOAD_PRINT_STOCK_ORDERS(symbol=None):
    if symbol:
        func=r.find_stock_orders(symbol=symbol)
    else:
        func=r.get_all_stock_orders()
    print(FORMAT_ORDER_STOCKS(func))
    return func

# LOAD + PRINT CRYPTO ORDER OF A SYMBOL OR ALL <- old split these up below (maybe delete)
def LOAD_PRINT_CRYPTO_ORDERS():
    func=r.get_all_crypto_orders()
    print(FORMAT_ORDER_CRYPTOS(func))
    return func

# LOAD + PRINT OPTIONS ORDER OF A SYMBOL OR ALL - might not work <- old split these up below (maybe delete)
def LOAD_PRINT_OPTION_ORDERS():
    func=r.get_all_option_orders()
    print(FORMAT_ORDER_OPTIONS(func))
    return func

###################

# PRINT STOCK ORDERS OF A SYMBOL OR ALL
def PRINT_STOCK_ORDERS(RS_orders):
    print(FORMAT_ORDER_STOCKS(RS_orders))

# PRINT CRYPTO ORDER OF A SYMBOL OR ALL
def PRINT_CRYPTO_ORDERS(RS_orders):
    print(FORMAT_ORDER_CRYPTOS(RS_orders))

# PRINT OPTIONS ORDER OF A SYMBOL OR ALL - might not work
def PRINT_OPTION_ORDERS(RS_orders):
    print(FORMAT_ORDER_OPTIONS(RS_orders))

###################

# LOAD STOCK ORDERS OF A SYMBOL OR ALL
def LOAD_STOCK_ORDERS(symbol=None):
    if symbol:
        func=r.find_stock_orders(symbol=symbol)
    else:
        func=r.get_all_stock_orders()
    return func

# LOAD CRYPTO ORDER OF A SYMBOL OR ALL
def LOAD_CRYPTO_ORDERS():
    func=r.get_all_crypto_orders()
    return func

# LOAD OPTIONS ORDER OF A SYMBOL OR ALL - might not work
def LOAD_OPTION_ORDERS():
    func=r.get_all_option_orders()
    return func

###################

# PARSE STOCK ORDERS
def PARSE_STOCK_ORDERS(RS_stock_orders):
    stock_order_dict = {}
    for o in RS_stock_orders:
        symbol = URL2SYM(o["instrument"])
        order = orders.order(o["last_transaction_at"],o["side"],float(o["average_price"]),float(o["quantity"]))
        if symbol in stock_order_dict:
            # if symbol already exists just add order
            stock_order_dict[symbol].add_order(order)
        else:
            # if symbol not in dict, create new instance of stock_orders and put 1 order 
            stock_order_dict[symbol] = orders.multi_orders(symbol, [order])
    return stock_order_dict

# PARSE CRYPTO ORDERS
def PARSE_CRYPTO_ORDERS(RS_crypto_orders):
    crypto_order_dict = {}
    for o in RS_crypto_orders:
        symbol = ID2SYM(o["currency_pair_id"],cryptopairs)
        order = orders.order(o["last_transaction_at"],o["side"],float(o["average_price"]),float(o["quantity"]))
        if symbol in crypto_order_dict:
            crypto_order_dict[symbol].add_order(order)
        else:
            crypto_order_dict[symbol] = orders.multi_orders(symbol, [order])
    return crypto_order_dict

# TODO: PARSE OPTION ORDERS (maybe going to be like stocks?)
def PARSE_OPTION_ORDERS(RS_option_orders):
    pass

###################

# PRINT STOCKS + ORDERS
def PRINT_ALL_PROFILE_AND_ORDERS():

    # print date header
    print(f"Date: {run_date}")

    # print account info
    prof_type = ["account","basic","investment","portfolio","security","user"]

    for prof in prof_type:
        print(f"---{prof} Profile---")
        prof_func = getattr(r.profiles,f"load_{prof}_profile")
        print("\n".join([ f"* {i[0]}: {i[1]}" for i in prof_func().items() ]))
        print()

    # print account values
    print(f"--- Gain Information (Beta) ---")
    print(f"NOTE: Currently not taking into account cash_management, options, and crypto. If you are doing pure stocks, this is accurate.")
    profileData = r.load_portfolio_profile()
    allTransactions = r.get_bank_transfers()
    cardTransactions= r.get_card_transactions()

    deposits = sum(float(x['amount']) for x in allTransactions if (x['direction'] == 'deposit') and (x['state'] == 'completed'))
    withdrawals = sum(float(x['amount']) for x in allTransactions if (x['direction'] == 'withdraw') and (x['state'] == 'completed'))
    debits = sum(float(x['amount']['amount']) for x in cardTransactions if (x['direction'] == 'debit' and (x['transaction_type'] == 'settled')))
    reversal_fees = sum(float(x['fees']) for x in allTransactions if (x['direction'] == 'deposit') and (x['state'] == 'reversed'))

    money_invested = deposits + reversal_fees - (withdrawals - debits)
    dividends = r.get_total_dividends()
    percentDividend = dividends/money_invested*100

    equity = float(profileData['equity'])  # author original was extended_hours_equity
    extended_hours_equity_string = profileData['extended_hours_equity']
    try:
        extended_hours_equity = float(extended_hours_equity_string)
        use_equity = extended_hours_equity
        print("* Sidenote: extended_hours_equity exists, using it")
    except:
        extended_hours_equity = None
        use_equity = equity
        print("* Sidenote: extended_hours_equity missing, using regular equity instead")
        
    totalGainMinusDividends = use_equity - dividends - money_invested # missing cash_account_debits + i think also missing crypto and options
    percentGain = totalGainMinusDividends/money_invested*100

    print(f"* Reported Deposits: {TOMONEY(deposits)}")
    print(f"* Reported Withdrawals: {TOMONEY(withdrawals)}")
    print(f"* Reported Debits: {TOMONEY(debits)} *** this is wrong right now ***") # <-- why is this 0, it should be all cash_account debits
    print(f"* Reported Reversal Fees: {TOMONEY(reversal_fees)}")
    print(f"* The total money invested is {TOMONEY(money_invested)}")
    print(f"* The total equity is {TOMONEY(equity)}")
    print(f"* Sidenote: extended_hours_equity is {TOMONEY(extended_hours_equity)}") # added by me
    print(f"* The net worth has increased {percentDividend:.3f}% due to dividends that amount to {TOMONEY(dividends)}")
    print(f"* The net worth has increased {TOMONEY(percentGain)}% due to other gains that amount to {TOMONEY(totalGainMinusDividends)}")
    print()

    # print load stock + crypto + options - TIME CONSUMING
    print(f"--- Loading Orders ---")
    print(f"* (S) started stock orders load")
    stock_orders = LOAD_STOCK_ORDERS()
    print(f"* (S) completed stock orders load")
    print(f"* (C) started crypto orders load")
    crypto_orders = LOAD_CRYPTO_ORDERS()
    print(f"* (C) completed crypto orders load")
    print(f"* (O) started option orders load")
    option_orders = LOAD_OPTION_ORDERS()
    print(f"* (O) completed option orders load")
    print()

    # print all stock orders (buy and sell)
    stocks_dict = {}
    print(f"--- All Stock Orders ---")
    PRINT_STOCK_ORDERS(stock_orders)
    stocks_dict = PARSE_STOCK_ORDERS(stock_orders) # TODO
    print()

    # print all crypto orders (buy and sell)
    cryptos_dict = {}
    print(f"--- All Crypto Orders ---")
    PRINT_CRYPTO_ORDERS(crypto_orders)
    cryptos_dict = PARSE_CRYPTO_ORDERS(crypto_orders)  # TODO
    print()

    # print all option orders (buy and sell)
    options_dict = {}
    print(f"--- All Option Orders ---")
    PRINT_OPTION_ORDERS(option_orders)
    options_dict = PARSE_OPTION_ORDERS(option_orders)  # TODO
    print()

    # TODO: show my calculations of profit for stock, crypto, options + total

###################

####### MAIN ######

###################

# currently want to run this part of the code if imported and not imported
LOGIN() # gives us r
cryptopairs = r.get_crypto_currency_pairs() # global var

if __name__ == "__main__":

    # args

    arg_desc = f"rhood v{Version} - provides lots of robinhood information"
    parser = argparse.ArgumentParser(description=arg_desc)
    parser.add_argument("--info","-i",help="get all profile + order info",action="store_true")
    args = parser.parse_args()

    if args.info:
        PRINT_ALL_PROFILE_AND_ORDERS()
        sys.exit(0)

    # ran without options
    # print("Ran without options. It just logged in. Best to run interactively:\nexample 1: python -i rhood.py\nexample 2: ipython -i rhood.py")

# EOF
