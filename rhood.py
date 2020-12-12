#!/usr/bin/env python
import robin_stocks as r
import pyotp
import sys
import json
import base64
import datetime
import argparse
import orders
import pickle
import os.path
import os
import csv

###################
#### PRE VARS #####
###################

# global vars
Version="0.0.11"
run_date = datetime.datetime.now()
run_date_orders = None # its set later either to run_date or loaded run_date, we establish it here so that its global
FILENAME = "dat.pkl"
CREDENTIALSFILE = "creds-encoded"

###################
#### FUNCTIONS ####
###################

# LOGIN
def LOGIN():
    global r
    if not os.path.isfile(CREDENTIALSFILE):
        print()
        print(f"* ERROR: credentials file missing in current path '{CREDENTIALSFILE}'. follow README.md for creation instructions.")
        print()
        sys.exit(-1)
    with open(CREDENTIALSFILE) as f:
        lines = base64.b64decode(f.read()).decode("utf-8").split()
    # lines = open("creds").readlines() # much less secure (creds file has 3 lines, email/username, password, authkey)
    EMAIL, PASSWD, KEY = map(lambda x: x.strip(), lines)
    ptot = pyotp.TOTP(KEY)
    ptot_now = ptot.now()
    login = r.login(EMAIL,PASSWD,mfa_code=ptot_now)
    return login

###################

# GET LATEST PRICE OF STOCK
def QUOTE_STOCK(symbol):
    ans=r.get_latest_price(symbol)
    return float(ans[0])

# BUY X SHARES OF STOCK
def BUY_STOCK(symbol, amount_of_shares):
    ans=r.order_buy_market(symbol,amount_of_shares)
    return ans

# SELL X SHARES OF STOCK
def SELL_STOCK(symbol, amount_of_shares):
    ans=r.order_buy_market(symbol,amount_of_shares)
    return ans

###################

# GET LATEST CRYPTO PRICE
def QUOTE_CRYPTO(symbol):
    ans=r.get_crypto_quote(symbol)
    return float(ans["ask_price"])

###################

# SIMPLE CONVERT INSTRUMENT URL TO SYMBOL
def URL2SYM(url):
    return r.get_symbol_by_url(url)

# CONVERT CURRENCY ID TO NAME
def ID2SYM(id,cryptopairs):
    for i in cryptopairs:
        if i["id"] == id:
            return i["asset_currency"]["code"] # old: i["symbol"] used to be BTC-USD, new: its just BTC

###################

# CONVERT MONEY STRING TO 2 DECIMAL 
def TOMONEY(money_string):
    if money_string is None:
        return "None"
    else:
        return f"{float(money_string):.2f}"

# CONVERT TO 2 POINT DECIMAL FLOAT
def D2(number):
     return f"{float(number):.2f}"

# CONVERT TO X POINT DECIMAL FLOAT
def DX(number,number_of_decimals):
     return f"{float(number):.{number_of_decimals}f}"

###################

# FORMAT STOCKS ORDERS TO EXTRA INFORMATION STRING
def FORMAT_ORDER_STOCKS(RS_orders):
    # return "\n".join([ f'{o["last_transaction_at"]} - {o["id"]} - {o["side"]}\tx{o["quantity"]}\t{URL2SYM(o["instrument"])} [S|{o["state"]}]\tavg: ${TOMONEY(o["average_price"])}\texec1/{len(o["executions"])}: ${TOMONEY(o["executions"][0]["price"])}\tprice: ${TOMONEY(o["price"])}' for o in RS_orders ])
    if RS_orders is None:
        return
    result = ""
    for o in RS_orders:
        date = o["last_transaction_at"]
        id = o["id"]
        side = o["side"]
        quantity = o["quantity"]
        symbol = URL2SYM(o["instrument"])
        state = o["state"]
        priceavg = TOMONEY(o["average_price"])
        execs = len(o["executions"]) if state != "cancelled" else "None"
        price1 = TOMONEY(o["executions"][0]["price"]) if state != "cancelled" else "None"
        price = TOMONEY(o["price"])
        result += f'{date} - {id} - {side}\tx{quantity}\t{symbol} [S|{state}]\tavg: ${priceavg}\texec1/{execs}: ${price1}\tprice: ${price}\n'
    return result


# FORMAT CRYPTOS ORDERS TO EXTRA INFORMATION STRING
def FORMAT_ORDER_CRYPTOS(RS_orders):
    # return "\n".join([ f'{o["last_transaction_at"]} - {o["id"]} - {o["side"]}\t${TOMONEY(o["rounded_executed_notional"])}\tx{o["quantity"]}\t{ID2SYM(o["currency_pair_id"],cryptopairs)} [C|{o["state"]}]\tavg: ${TOMONEY(o["average_price"])}\texec1/{len(o["executions"])}: ${TOMONEY(o["executions"][0]["effective_price"])}\tprice: ${TOMONEY(o["price"])}' for o in RS_orders ])
    if RS_orders is None:
        return
    result = ""
    for o in RS_orders:
        date = o["last_transaction_at"]
        id = o["id"]
        side = o["side"]
        rounded = TOMONEY(o["rounded_executed_notional"])
        quantity = o["quantity"]
        symbol = ID2SYM(o["currency_pair_id"],cryptopairs)
        state = o["state"]
        priceavg = TOMONEY(o["average_price"])
        execs = len(o["executions"]) if state != "cancelled" else "None"
        price1 = TOMONEY(o["executions"][0]["effective_price"]) if state != "cancelled" else "None"
        price = TOMONEY(o["price"])
        result += f'{date} - {id} - {side}\t${rounded}\tx{quantity}\t{symbol} [C|state]\tavg: ${priceavg}\texec1/{execs}: ${price1}\tprice: ${price}\n'
    return result


# FORMAT OPTIONS ORDERS TO EXTRA INFORMATION STRING - TODO: test with options one date. might be similar to stocks just change to O in state field
def FORMAT_ORDER_OPTIONS(RS_orders):
    pass

###################

def PRINT_ORDERS_DICTIONARY(stock_orders_dictionary):
    if stock_orders_dictionary is None:
        return
    len_of_stocks = len(stock_orders_dictionary)
    stock_num = 0
    total_order_num = 0
    for symbol, obj in stock_orders_dictionary.items():
        stock_num += 1
        stock_order_num = 0
        len_of_orders = len(obj.orders)
        for order in obj.orders:
            total_order_num += 1;
            stock_order_num += 1
            print(f"* sym# {stock_num}/{len_of_stocks} ord# {stock_order_num}/{len_of_orders} tot_ord# {total_order_num} - {order.date_nice()} - {symbol} - {order.type_string} - x{order.amount_float} at ${DX(order.amount_float,4)} - value ${D2(order.value_float)}")

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

# sort all stock, crypto, options increasing time
def SORT_ALL_DICT_ORDERS_INCREASING(dict_of_symbol_orders):
    for i in dict_of_symbol_orders.values():
        i.sort_by_time_increasing()

# sort all stock, crypto, options decreasing time
def SORT_ALL_DICT_ORDERS_DECREASING(dict_of_symbol_orders):
    for i in dict_of_symbol_orders.values():
        i.sort_by_time_decreasing()

###################

# PARSE STOCK ORDERS
def PARSE_STOCK_ORDERS(RS_stock_orders):
    stock_order_dict = {}
    for o in RS_stock_orders:
        if o["state"] == "cancelled":
            continue
        symbol = URL2SYM(o["instrument"])
        order = orders.order(o["last_transaction_at"],o["side"],float(o["average_price"]),float(o["quantity"]))
        if symbol in stock_order_dict:
            # if symbol already exists just add order
            stock_order_dict[symbol].add_order(order)
        else:
            # if symbol not in dict, create new instance of stock_orders and put 1 order 
            stock_order_dict[symbol] = orders.multi_orders(symbol, [order])
    SORT_ALL_DICT_ORDERS_INCREASING(stock_order_dict)
    return stock_order_dict

# PARSE CRYPTO ORDERS
def PARSE_CRYPTO_ORDERS(RS_crypto_orders):
    crypto_order_dict = {}
    for o in RS_crypto_orders:
        if o["state"] == "cancelled":
            continue
        symbol = ID2SYM(o["currency_pair_id"],cryptopairs)
        order = orders.order(o["last_transaction_at"],o["side"],float(o["average_price"]),float(o["quantity"]))
        if symbol in crypto_order_dict:
            crypto_order_dict[symbol].add_order(order)
        else:
            crypto_order_dict[symbol] = orders.multi_orders(symbol, [order])
    SORT_ALL_DICT_ORDERS_INCREASING(crypto_order_dict)
    return crypto_order_dict

# TODO: PARSE OPTION ORDERS (maybe going to be like stocks?)
def PARSE_OPTION_ORDERS(RS_option_orders):
    pass

###################

# save time consuming data to file
def save_data(filename,so,co,oo,sd,cd,od,soo,coo,ooo,verify_bool=False):
    save_data = { "stock_orders":so, "crypto_orders":co, "option_orders":oo, "stocks_dict":sd, "cryptos_dict":cd, "options_dict":od, "stocks_open":soo, "cryptos_open":coo, "options_open":ooo, "run_date": run_date }
    # Store data (serialize)
    with open(filename, 'wb') as handle:
        pickle.dump(save_data, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # verify save
    if verify_bool:
        ld = load_data(filename)
        len_so = len(ld["stock_orders"]) if ld["stock_orders"] is not None else 0
        len_co = len(ld["crypto_orders"]) if ld["crypto_orders"] is not None else 0
        len_oo = len(ld["option_orders"]) if ld["option_orders"] is not None else 0
        len_sd = len(ld["stocks_dict"]) if ld["stocks_dict"] is not None else 0
        len_cd = len(ld["cryptos_dict"]) if ld["cryptos_dict"] is not None else 0
        len_od = len(ld["options_dict"]) if ld["options_dict"] is not None else 0
        len_soo = len(ld["stocks_open"]) if ld["stocks_open"] is not None else 0
        len_coo = len(ld["cryptos_open"]) if ld["cryptos_open"] is not None else 0
        len_ooo = len(ld["options_open"]) if ld["options_open"] is not None else 0
        print()
        print(f"* saved data to {filename} of run_date {run_date} - {len_so} orders of {len_soo} open of {len_sd} stocks - {len_co} orders of {len_coo} open of {len_cd} crypto - {len_oo} orders of {len_ooo} open of {len_od} options")
        print()

# load time consuming data from file
def load_data(filename):
    # check if file exists
    if not os.path.isfile(filename):
        print()
        print(f"* ERROR: can't load {filename}, it is missing. try running with --save parameter instead so that we contact the API for the order information and save the data to {filename}.")
        print()
        sys.exit(-1)
    # Load data (deserialize)
    with open(filename, 'rb') as handle:
        unserialized_data = pickle.load(handle)
    return unserialized_data

###################

# csv functions

# print list of dictionary to file name csv (works for stocks, crypto and options + anything really)
def print_to_csv(fname, list_of_dictionary):
    # global run_date_orders
    # create dir and get filename
    dir_suffix = "csv"
    date_string = run_date_orders.strftime("%Y%m%d-%H%M")
    dir_full = dir_suffix+"/"+ date_string
    if not os.path.exists(dir_suffix):
        os.makedirs(dir_suffix)
    if not os.path.exists(dir_full):
        os.makedirs(dir_full)
    filename = dir_full + "/" + fname + ".csv"
    # csv saving
    toCSV = list_of_dictionary
    keys = toCSV[0].keys()
    with open(filename, 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(toCSV)

# print all stock orders csvs
def print_all_stocks_to_csv(RS_orders_all_stocks):
    # stocks are IDed by their instrument, get all of the unique instruments with a set
    instruments = set()
    for o in RS_orders_all_stocks:
        instruments.add(o["instrument"])
    # go thru each symbol and make csv
    for i in instruments:
        symbol = URL2SYM(i)
        current_orders = [ j for j in RS_orders_all_stocks if j["instrument"]==i ]
        print_to_csv("S-"+symbol,current_orders)
    # print all stocks (for fun)
    print_to_csv("S-(all)",RS_orders_all_stocks)

# print all crypto orders csvs
def print_all_crypto_to_csv(RS_orders_all_cryptos):
    # crypto are IDed by their currency_pair_id, get all of the unique ones with a set
    currency_pair_ids = set()
    for o in RS_orders_all_cryptos:
        currency_pair_ids.add(o["currency_pair_id"])
    # go thru each symbol and make csv
    for i in currency_pair_ids:
        symbol = ID2SYM(i,cryptopairs)
        current_orders  = [ j for j in RS_orders_all_cryptos if j["currency_pair_id"]==i ]
        print_to_csv("C-"+symbol,current_orders)
    # print all stocks (for fun)
    print_to_csv("C-(all)",RS_orders_all_cryptos)


# print all options orders csvs - TODO: create + test when we get options. remember to prefix with "O" for options
def print_all_options_to_csv(RS_orders_all_options):
    pass

###################

# PRINT STOCKS + ORDERS
def PRINT_ALL_PROFILE_AND_ORDERS(save_bool=False,load_bool=False, extra_info_bool=False, csv_bool=False):

    global run_date_orders # we change this value in here so we mark it as changeable with global keyword

    # print date header
    print(f"Date: {run_date} - Rhood Version: {Version}")
    print()

    # print account info
    prof_type = ["account","basic","investment","portfolio","security","user"]

    for prof in prof_type:
        print(f"---{prof} Profile---")
        prof_func = getattr(r.profiles,f"load_{prof}_profile")
        print("\n".join([ f"* {i[0]}: {i[1]}" for i in prof_func().items() ]))
        print()

    # print account values
    print(f"--- Gain Information (Beta) ---")
    print(f"* NOTE: Currently not taking into account cash_management, options, and crypto. If you are doing only stocks, then this section is accurate.")
    print(f"* NOTE: The profit calculations below this section are more accurate as they look into every symbols order + current open positions")
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
    if extended_hours_equity_string is not None:
        extended_hours_equity = float(extended_hours_equity_string)
        use_equity = extended_hours_equity
        print("* NOTE: extended_hours_equity exists, using it")
    else:
        extended_hours_equity = None
        use_equity = equity
        print("* NOTE: extended_hours_equity missing, using regular equity instead")
        
    totalGainMinusDividends = use_equity - dividends - money_invested # missing cash_account_debits + i think also missing crypto and options
    percentGain = totalGainMinusDividends/money_invested*100

    print(f"* Reported Deposits: {TOMONEY(deposits)}")
    print(f"* Reported Withdrawals: {TOMONEY(withdrawals)}")
    print(f"* Reported Debits: {TOMONEY(debits)} *** this is wrong right now ***") # <-- why is this 0, it should be all cash_account debits
    print(f"* Reported Reversal Fees: {TOMONEY(reversal_fees)}")
    print(f"* The total money invested is {TOMONEY(money_invested)}")
    print(f"* The total equity is {TOMONEY(equity)}")
    print(f"* NOTE: extended_hours_equity is {TOMONEY(extended_hours_equity)}") # added by me
    print(f"* The net worth has increased {percentDividend:.3f}% due to dividends that amount to {TOMONEY(dividends)}")
    print(f"* The net worth has increased {TOMONEY(percentGain)}% due to other gains that amount to {TOMONEY(totalGainMinusDividends)} *** correct if only stocks & no cash mgmt ***")
    print()

    # print load stock + crypto + options - TIME CONSUMING
    if load_bool:
        # loading orders from pickle
        # no need to reverse, as we already saveed reversed
        print(f"--- Loading Orders (from file) ---")
        ld = load_data(FILENAME) # this is used below this if as well
        run_date_orders = ld['run_date']
        print(f"* loaded order data from '{FILENAME}' which ran on {run_date_orders}")
        print(f"* (S) started stock orders load")
        stock_orders = ld["stock_orders"]
        print(f"* (S) completed stock orders load")
        print(f"* (C) started crypto orders load")
        crypto_orders = ld["crypto_orders"]
        print(f"* (C) completed crypto orders load")
        print(f"* (O) started option orders load")
        option_orders = ld["option_orders"]
        print(f"* (O) completed option orders load")
        print()
    else:
        # contacting order via API
        print(f"--- Loading Orders (from API) ---")
        run_date_orders = run_date
        print(f"* loading orders via API on {run_date_orders}")
        print(f"* (S) started stock orders load")
        stock_orders = LOAD_STOCK_ORDERS()
        stock_orders.reverse()
        print(f"* (S) completed stock orders load")
        print(f"* (C) started crypto orders load")
        crypto_orders = LOAD_CRYPTO_ORDERS()
        crypto_orders.reverse()
        print(f"* (C) completed crypto orders load")
        print(f"* (O) started option orders load")
        option_orders = LOAD_OPTION_ORDERS()
        option_orders.reverse()
        print(f"* (O) completed option orders load")
        print()

    # print all stock orders (buy and sell)
    stocks_dict = {}
    print(f"--- All Stock Orders ---")
    if stock_orders != []:
        if extra_info_bool: # time consuming shows alot of extra information (like state of orders and more)
            PRINT_STOCK_ORDERS(stock_orders)  ## time consuming
            print()
            if load_bool:
                print("...loading parsed stock orders...")
                stocks_dict = ld["stocks_dict"]
            else:
                print("...parsing stock orders...")
                stocks_dict = PARSE_STOCK_ORDERS(stock_orders)
            print()
            print(f"--- Parsed Fulfilled Stock Orders ---")
            PRINT_ORDERS_DICTIONARY(stocks_dict)
            print()
        else: # not time consuming
            if load_bool:
                print("...loading parsed stock orders...")
                stocks_dict = ld["stocks_dict"]
            else:
                print("...parsing stock orders...")
                stocks_dict = PARSE_STOCK_ORDERS(stock_orders)
            PRINT_ORDERS_DICTIONARY(stocks_dict)
            print()

    # print all crypto orders (buy and sell)
    cryptos_dict = {}
    print(f"--- All Crypto Orders ---")
    if crypto_orders != []:
        if extra_info_bool: # time consuming shows alot of extra information (like state of orders and more)
            PRINT_CRYPTO_ORDERS(crypto_orders) ## time consuming
            print()
            if load_bool:
                print("...loading parsed crypto orders...")
                cryptos_dict = ld["cryptos_dict"]
            else:
                print("...parsing crypto orders...")
                cryptos_dict = PARSE_CRYPTO_ORDERS(crypto_orders)
            print()
            print(f"--- Parsed Fulfilled Crypto Orders ---")
            PRINT_ORDERS_DICTIONARY(cryptos_dict)
            print()
        else: # not time consuming
            if load_bool:
                print("...loading parsed crypto orders...")
                cryptos_dict = ld["cryptos_dict"]
            else:
                print("...parsing crypto orders...")
                cryptos_dict = PARSE_CRYPTO_ORDERS(crypto_orders)
            PRINT_ORDERS_DICTIONARY(cryptos_dict)
            print()

    # print all option orders (buy and sell)
    options_dict = {}
    print(f"--- All Option Orders ---")
    if option_orders != []: # time consuming shows alot of extra information (like state of orders and more)
        PRINT_OPTION_ORDERS(option_orders)  ## time consuming
        print()
        if load_bool:
            print("...loading parsed option orders...")
            options_dict = ld["options_dict"]
        else:
            print("...parsing option orders...")
            options_dict = PARSE_OPTION_ORDERS(option_orders)
        print()
        print(f"--- Parsed Fulfilled Option Orders ---")
        PRINT_ORDERS_DICTIONARY(options_dict)
        print()
    else:  # not time consuming
        if load_bool:
            print("...loading parsed option orders...")
            options_dict = ld["options_dict"]
        else:
            print("...parsing option orders...")
            options_dict = PARSE_OPTION_ORDERS(option_orders)
        PRINT_ORDERS_DICTIONARY(options_dict)
        print()

    # quick inner function:
    def show_profits_from_orders_dictionary(dictionary):
        total_profit = 0
        total_amount = 0
        for sym,orders in dictionary.items():
            last_profit = orders.latest_profit()
            last_amount = orders.latest_amount()
            print(f"* {sym} net profit ${D2(last_profit)}")
            total_profit += last_profit
            total_amount += last_amount
        print(f"* total net profit ${D2(total_profit)}")
        return (total_profit, total_amount)

    # show open positions
    print("--- Open Positions ---")
    total_stocks_open_amount, total_cryptos_open_amount, total_options_open_amount = (0, 0, 0)
    total_stocks_open_value, total_cryptos_open_value, total_options_open_value = (0, 0, 0)
    sod, cod, ood = [], [], [] # stock open dict, crypto open dict, option open dict
    # stocks
    stocks_open = ld["stocks_open"] if load_bool else r.get_open_stock_positions() 
    if stocks_open != []:
        print()
        for i in stocks_open:
            s = URL2SYM(i["instrument"])
            a = float(i["quantity"])
            p = QUOTE_STOCK(s) # or maybe faster to do this: float(i["average_buy_price"])
            stocks_dict[s].update_current(a,p)
            total_stocks_open_amount += a
            total_stocks_open_value += stocks_dict[s].current_value
            sod.append({ "symbol": s, "quantity": a, "price": p, "value": stocks_dict[s].current_value })
            print(f"* OPEN STOCK - {s} x{stocks_dict[s].current_amount} at ${D2(stocks_dict[s].current_avgprice)} each - est current value: ${D2(stocks_dict[s].current_value)}")
        print(f"* TOTAL OPEN STOCKS - {total_stocks_open_amount} stocks for total ${D2(total_stocks_open_value)} estimated value")
    # cryptos
    cryptos_open = ld["cryptos_open"] if load_bool else r.get_crypto_positions()
    if cryptos_open != []:
        print()
        for i in cryptos_open:
            s = i["currency"]["code"] 
            a = float(i["quantity"])
            p = QUOTE_CRYPTO(s)
            cryptos_dict[s].update_current(a,p)
            total_cryptos_open_amount += a
            total_cryptos_open_value += cryptos_dict[s].current_value
            cod.append({ "symbol": s, "quantity": a, "price": p, "value": cryptos_dict[s].current_value })
            print(f"* OPEN CRYPTO - {s} x{cryptos_dict[s].current_amount} at ${D2(cryptos_dict[s].current_avgprice)} each - est current value: ${D2(cryptos_dict[s].current_value)}")
        print(f"* TOTAL OPEN CRYPTO - {total_cryptos_open_amount} stocks for total ${D2(total_cryptos_open_value)} estimated value")
    # TODO: options open positions
    options_open = ld["options_open"] if load_bool else r.get_all_option_positions()
    if options_open != []:
        pass
    # show total open amounts
    if stocks_open != [] or cryptos_open != [] or stocks_open != []:
        total_open_amount = total_stocks_open_amount, total_cryptos_open_amount, total_options_open_amount
        total_open_value = total_stocks_open_value + total_cryptos_open_value + total_options_open_value
        print()
        print(f"* TOTAL OPEN POSITIONS VALUE: ${D2(total_open_value)}")

    # show each stocks profit
    print()
    print(f"--- Profits Based On Orders + Open Positions ---")
    print("* NOTE: For this profit approximation, we add up all of the sell values, subtract the buy values, and finally add back in the current open value (if there are any stocks) If a stock is open, we assume it is all sold at current value.")
    print("* NOTE: profit per stock = current open position value + sum of all of the sells - sum of all of the buy orders")
    total_stocks_profit, total_stocks_amount, total_cryptos_profit, total_cryptos_amount, total_options_profit, total_options_amount = (0,0,0,0,0,0)
    if stock_orders != []:
        print()
        print(f"STOCKS:")
        total_stocks_profit, total_stocks_amount = show_profits_from_orders_dictionary(stocks_dict)
    if crypto_orders != []:
        print()
        print(f"CRYPTO:")
        total_cryptos_profit, total_cryptos_amount = show_profits_from_orders_dictionary(cryptos_dict)
    if option_orders != []:
        print()
        print(f"OPTIONS:")
        total_options_profit, total_options_amount = show_profits_from_orders_dictionary(options_dict)
    complete_profit = total_stocks_profit + total_cryptos_profit + total_options_profit
    print()
    print("TOTAL NET PROFIT STOCKS + CRYPTO + OPTIONS:")
    print(f"* total net profit from stocks, crypto, and options: ${D2(complete_profit)}")
    print()

    # print extra info footer
    print(f"--- Final Notes ---")
    if load_bool:
        print(f"* loaded order data from '{FILENAME}' which ran on {run_date_orders}")
    else:
        print(f"* loaded order data from robinhood API run date {run_date_orders}")

    # create csv here if we wanted to
    if csv_bool:
        if stock_orders != []:
            print("* saving stock orders + open positions csvs")
            print_all_stocks_to_csv(stock_orders)
            if sod != []:
                print_to_csv("All-Open-Stocks",sod)
            print(f"* saved stock csvs")
        if crypto_orders != []:
            print("* saving crypto + open positions csvs")
            print_all_crypto_to_csv(crypto_orders)
            if cod != []:
                print_to_csv("All-Open-Crypto",cod)
            print(f"* saved crypto csvs")
        if option_orders != []:
            print("* saving option + open positions csvs")
            print_all_options_to_csv(option_orders)
            if ood != []:
                print_to_csv("All-Open-Options",ood)
            print(f"* saved option csvs")

    # Save Data
    if save_bool:
        save_data(FILENAME, so = stock_orders, co = crypto_orders, oo = option_orders, sd = stocks_dict, cd = cryptos_dict, od = options_dict, soo = stocks_open, coo = cryptos_open, ooo = options_open, verify_bool = True)

###################
####### MAIN ######
###################

# currently want to run this part of the code if imported and not imported
LOGIN() # gives us r
cryptopairs = r.get_crypto_currency_pairs() # global var

if __name__ == "__main__":

    # args parser

    arg_desc = f"rhood v{Version} - provides lots of robinhood information"
    parser = argparse.ArgumentParser(description=arg_desc)
    parser.add_argument("--info","-i",help="get all profile + order info",action="store_true")
    parser.add_argument("--save","-s",help="save all orders to file (dat.pkl) if --info is used.",action="store_true")
    parser.add_argument("--load","-l",help="load all orders to file (dat.pkl) if --info is used (uses saved file instead of API to get order info; saving time)",action="store_true")
    parser.add_argument("--extra","-e",help="shows extra order information (time consuming)",action="store_true")
    parser.add_argument("--csv","-c",help="save all loaded orders to csv files in 'csv' directory (dir is created if missing)", action="store_true")
    args = parser.parse_args()

    # parse save and load
    save_bool = args.save
    load_bool = args.load

    # extra information
    extra_info_bool = args.extra

    # save csv of orders
    csv_bool = args.csv

    # error checking on saving and loading
    if load_bool and save_bool:
        print()
        print("* ERROR: can't save and load. try again with either save or load.")
        print()
        sys.exit(-1)

    if args.info:
        # get main
        PRINT_ALL_PROFILE_AND_ORDERS(save_bool=save_bool, load_bool=load_bool, extra_info_bool=extra_info_bool,csv_bool=csv_bool)

# EOF