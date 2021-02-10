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
Version="0.2.0"
run_date = datetime.datetime.now()
run_date_orders = None # its set later either to run_date or loaded run_date, we establish it here so that its global
CREDENTIALSFILE = "creds-encoded" # file we read for creds
FILENAME = "dat.pkl" # where we order info
dir_suffix = "csv" # where we save csvs
user_string = ""
expires_seconds = 3600 # one hour login session (don't worry they don't overlap so you can login with another user afterwards)
loaded_username = ""
cryptopairs = None

###################
#### FUNCTIONS ####
###################

# LOGIN WITH 2FACTOR. creds FILE HAS 3 LINES: username/email, password, authkey
def LOGIN(un="",pw="",ke=""):
    global r, user_string, loaded_username
    if un != "" and pw != "" and ke != "":
        # CLI LOGIN
        EMAIL, PASSWD, KEY = un, pw, ke
    elif un == "" and pw == "" and ke == "":
        # CREDS FILE
        if not os.path.isfile(CREDENTIALSFILE):
            print()
            print(f"* ERROR: Credentials file missing in current path '{CREDENTIALSFILE}'. Follow README.md for creation instructions.")
            print()
            sys.exit(1)
        with open(CREDENTIALSFILE) as f:
            lines = base64.b64decode(f.read()).decode("utf-8").split()
        # lines = open("creds").readlines() # much less secure (creds file has 3 lines, email/username, password, authkey)
        EMAIL, PASSWD, KEY = map(lambda x: x.strip(), lines)
    else:
        # FAIL
        print()
        print(f"* ERROR: If using CLI arguments for secure login, must specify: username, password and authentication key.")
        print()
        sys.exit(1)
    # now we have creds, login in and such
    loaded_username = EMAIL
    user_string = EMAIL.split("@")[0] # get the username part of the email (or just the username if username was provided)
    ptot = pyotp.TOTP(KEY)
    ptot_now = ptot.now()
    # probably don't need this try block but it doesn't hurt - so we logout first
    try:
        r.logout()
    except:
        pass
    # login and don't store session to pickle file, so that we
    login = r.login(EMAIL, PASSWD, mfa_code=ptot_now, expiresIn = expires_seconds, store_session=False) # changed to store_session false so could load gabes data
    return login

# LOGIN INSECURELY WITHOUT 2FACTOR. creds FILE HAS 2 LINES: username/email, password
def LOGIN_INSECURE(un="",pw=""):
    global r, user_string, loaded_username
    if un != "" and pw != "":
        # CLI LOGIN
        EMAIL, PASSWD = un, pw
    elif un == "" and pw == "":
        # CREDS FILE
        if not os.path.isfile(CREDENTIALSFILE):
            print()
            print(f"* ERROR: Credentials file missing in current path '{CREDENTIALSFILE}'. Follow README.md for creation instructions.")
            print()
            sys.exit(1)
        with open(CREDENTIALSFILE) as f:
            lines = base64.b64decode(f.read()).decode("utf-8").split()
        # lines = open("creds").readlines() # much less secure (creds file has 3 lines, email/username, password)
        EMAIL, PASSWD = map(lambda x: x.strip(), lines)
    else:
        # FAIL
        print()
        print(f"* ERROR: If using CLI arguments for insecure login, must specify: username and password.")
        print()
        sys.exit(1)
    # now we have creds, login in and such
    loaded_username = EMAIL
    user_string = EMAIL.split("@")[0] # get the username part of the email (or just the username if username was provided)
    # probably don't need this try block but it doesn't hurt - so we logout first
    try:
        r.logout()
    except:
        pass
    # login and don't store session to pickle file, so that we
    login = r.login(EMAIL, PASSWD, expiresIn = expires_seconds, store_session=False) # changed to store_session false so could load gabes data
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
        execs = len(o["executions"]) if state == "filled" else "None"  # used to be state != "cancelled"
        price1 = TOMONEY(o["executions"][0]["price"]) if state == "filled" else "None"  # used to be state != "cancelled"
        price = TOMONEY(o["price"])
        result += f'* {date} - {id} - {side}\tx{quantity}\t{symbol} [S|{state}]\tavg: ${priceavg}\texec1/{execs}: ${price1}\tprice: ${price}\n'
    return result

# FORMAT CRYPTOS ORDERS TO EXTRA INFORMATION STRING
def FORMAT_ORDER_CRYPTOS(RS_orders):
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
        execs = len(o["executions"]) if state == "filled" else "None"  # used to be state != "cancelled"
        price1 = TOMONEY(o["executions"][0]["effective_price"]) if state == "filled" else "None"  # used to be state != "cancelled"
        price = TOMONEY(o["price"])
        result += f'* {date} - {id} - {side}\t${rounded}\tx{quantity}\t{symbol} [C|{state}]\tavg: ${priceavg}\texec1/{execs}: ${price1}\tprice: ${price}\n'
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
            print(f"* sym# {stock_num}/{len_of_stocks} ord# {stock_order_num}/{len_of_orders} tot_ord# {total_order_num} - {order.date_nice()} - {symbol} - {order.type_string} - x{order.amount_float} at ${DX(order.price_float,5)} - value ${D2(order.value_float)}")

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

# GET ALL CURRENTLY OPEN STOCKS - meaning we own these now
def LOAD_OPEN_STOCKS():
    func = r.get_open_stock_positions()
    return func

# GET ALL CURRENTLY OPEN CRYPTOS - meaning we own these now
def LOAD_OPEN_CRYPTOS():
    func = r.get_crypto_positions()
    return func

# GET ALL CURRENTLY OPEN OPTIONS - meaning we own these now
def LOAD_OPEN_OPTIONS():
    func = r.get_all_option_positions()
    return func

###################

# LOAD DIVIDENDS
def LOAD_DIVIDENDS():
    func=r.get_dividends()
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
        if o["state"] != "filled":  # used to be if o["state"] == "cancelled":
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
        if o["state"] != "filled":  # used to be if o["state"] == "cancelled":
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
# sod, cod, ood = list of dict of open positions { "symbol", "quantity", "price",  "value" }
def save_data(filename,so,co,oo,sd,cd,od,soo,coo,ooo,sod,cod,ood,divs,verify_bool=False):
    save_data = { "run_date": run_date, "username": loaded_username, "stock_orders":so, "crypto_orders":co, "option_orders":oo, "stocks_dict":sd, "cryptos_dict":cd, "options_dict":od, "stocks_open":soo, "cryptos_open":coo, "options_open":ooo, "sod":sod, "cod":cod, "ood": ood, "dividends":divs }  # loaded_username is global
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
        len_sod = len(ld["sod"]) if ld["sod"] is not None else 0
        len_cod = len(ld["cod"]) if ld["cod"] is not None else 0
        len_ood = len(ld["ood"]) if ld["ood"] is not None else 0
        len_divs = len(ld["dividends"]) if ld["dividends"] is not None else 0
        un = ld["username"] if ld["username"] is not None else "N/A"
        # print()
        # print(f"* saved data of {un} to {filename} of run_date {run_date} - {len_so} orders of {len_soo} open stocks of {len_sd} - {len_co} orders of {len_coo} open crypto of {len_cd} - {len_oo} orders of {len_ooo} open options of {len_od} - {len_divs} dividends")
        print(f"* saved data of {un} to {filename} of run_date {run_date} - (total orders, open symbols, total symbols): stocks ({len_so},{len_soo}/{len_sd}) - crypto ({len_co},{len_coo}/{len_cd}) - options ({len_oo},{len_ooo}/{len_od}) - {len_divs} dividends")
        print()

# load time consuming data from file
def load_data(filename):
    # check if file exists
    if not os.path.isfile(filename):
        print()
        print(f"* ERROR: Can't load {filename}, it is missing. Try running with --save parameter instead so that we contact the API for the order information and save the data to {filename}.")
        print()
        sys.exit(1)
    # Load data (deserialize)
    with open(filename, 'rb') as handle:
        unserialized_data = pickle.load(handle)
    return unserialized_data

###################

# get price from open positions list dict. list of { "symbol", "quantity", "price",  "value" }
def find_price_in_open_listdict(symbol,open_positions_list_dist):
    for i in open_positions_list_dist:
        if i["symbol"] == symbol:
            return i["price"]
    return None # we shouldnt return none (perhaps raise error)

###################

# csv functions
def get_save_dir():
    date_string = run_date_orders.strftime("%Y%m%d-%H%M")
    dir_full = f"{dir_suffix}/{date_string}-{user_string}"
    return dir_full

# list_of_dict_handle_missing_keys - looks thru a list of dictionary, gets all of thekys. lod is list of dictionaries
def list_of_dict_handle_missing_keys(lod):
    # from https://stackoverflow.com/questions/33910764/adding-missing-keys-in-dictionary-in-python
    empty_value = None # we replace all missing key values with this, we could also just put "NA" in string, but None is better as it turns to blank field in csv/excel
    L = lod
    allkeys = frozenset().union(*lod)
    for i in lod:
        for j in allkeys:
            if j not in i:
                i[j] = empty_value
    return L

# print list of dictionary or just a dictionary to filename (adds .csv to filename). toCSV is list of dicts, or dict (either or works)
def print_to_csv(fname, toCSV):
    # create dir and get filename
    dir_full = get_save_dir()
    if not os.path.exists(dir_suffix):
        os.makedirs(dir_suffix)
    if not os.path.exists(dir_full):
        os.makedirs(dir_full)
    filename = dir_full + "/" + fname + ".csv"
    # update / fix list of dictionaries to have common keys
    if isinstance(toCSV,list):
        toCSV=list_of_dict_handle_missing_keys(toCSV)
    # csv saving
    if isinstance(toCSV,list): # print list of dict
        keys = toCSV[0].keys()
        with open(filename, 'w', newline='')  as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(toCSV)
    if isinstance(toCSV,dict): # just print dict
        with open(filename, 'w') as f:
            for key in toCSV.keys():
                # f.write("%s,%s\n"%(key,toCSV[key]))
                f.write(f"{key},{toCSV[key]}\n")

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
def PRINT_ALL_PROFILE_AND_ORDERS(save_bool=False,load_bool=False, extra_info_bool=False, csv_bool=False, csv_profile_bool=False, info_type="ALL", sort_alpha_bool=False):

    global run_date_orders # we change this value in here so we mark it as changeable with global keyword

    # info type
    if info_type == "ALL":
        info_type_string = "All Information"
    elif info_type == "PROFILE":
        info_type_string = "Profile Information"
    elif info_type == "FINANCE":
        info_type_string = "Financial Information"

    # print date header
    print(f"Date: {run_date} - Rhood Version: {Version} - {info_type_string}")
    print()

    # preloading
    if load_bool:
        # loading orders from pickle
        ld = load_data(FILENAME) # this is used below this if as well
        run_date_orders = ld['run_date']
        print(f"* Preloading Complete")
        if ld["username"] != loaded_username:
            print()
            print(f"* ERROR: Loaded finance information of another user, can't do that. Please save current users data first using --save, if you wish to --load it at later point.")
            print()
            sys.exit(1)
        print()
    else:
        # contacting order via API
        run_date_orders = run_date

    if info_type == "ALL" or info_type == "PROFILE":
        # print account info
        prof_type = ["account","basic","investment","portfolio","security","user"]
        # save profiles to csv if csv_profile_bool
        for prof in prof_type:
            print(f"---{prof} Profile---")
            prof_func = getattr(r.profiles,f"load_{prof}_profile")
            prof_dictionary = prof_func()
            if csv_profile_bool:
                print_to_csv(f"A-{prof}-profile",prof_dictionary)
            print("\n".join([ f"* {i[0]}: {i[1]}" for i in prof_dictionary.items() ]))
            print()

    if info_type == "ALL" or info_type == "FINANCE":
        # print account values
        print(f"--- Gain Information (Experimental) ---")
        print(f"* NOTE: Currently this section does not take into account cash management, options, and crypto. If only stocks are involved, then this section _should_ be accurate.")
        print(f"* NOTE: The profit calculations in this section are inspired by https://github.com/jmfernandes/robin_stocks/blob/master/examples/get_accurate_gains.py")
        print(f"* NOTE: The profit calculations below this section are more accurate as they consider every symbol order + current open positions + dividends")

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
            print(f"* Loading orders via API on {run_date_orders}")
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

        # show open positions
        print("--- Open Positions ---")
        total_stocks_open_amount, total_cryptos_open_amount, total_options_open_amount = (0, 0, 0)
        total_stocks_open_value, total_cryptos_open_value, total_options_open_value = (0, 0, 0)
        sod, cod, ood = [], [], [] # stock open list of dicts, crypto open list of dicts, option open list of dicts
        # stocks
        stocks_open = ld["stocks_open"] if load_bool else LOAD_OPEN_STOCKS()
        sum_of_stocks_open_quantity = sum([ float(i["quantity"]) for i in stocks_open ])
        # if stocks_open != []:
        if sum_of_stocks_open_quantity != 0:
            print()
            print("STOCKS:")
            for i in stocks_open:
                s = URL2SYM(i["instrument"])
                a = float(i["quantity"])
                if a == 0: # skip if empty and not actually an open position
                    continue
                p = find_price_in_open_listdict(s,ld["sod"]) if load_bool else QUOTE_STOCK(s) # p = QUOTE_STOCK(s) # or maybe faster to do this: float(i["average_buy_price"])
                # print("DEBUG-S:",s,p)
                stocks_dict[s].update_current(a,p)
                total_stocks_open_amount += a
                total_stocks_open_value += stocks_dict[s].current_value
                sod.append({ "symbol": s, "quantity": a, "price": p, "value": stocks_dict[s].current_value })
            if sort_alpha_bool:
                sod.sort(key=lambda x: x["symbol"], reverse=False)
            else:
                sod.sort(key=lambda x: float(x["value"]), reverse=False)
            for i in sod:
                s = i["symbol"]
                a = i["quantity"]
                p = i["price"]
                v = i["value"]
                print(f"* OPEN STOCK - {s} x{a} at ${D2(p)} each - est current value: ${D2(v)}")
            print(f"* TOTAL OPEN STOCKS - {total_stocks_open_amount} stocks for total ${D2(total_stocks_open_value)} estimated value")
        # cryptos
        cryptos_open = ld["cryptos_open"] if load_bool else LOAD_OPEN_CRYPTOS()
        sum_of_cryptos_open_quantity = sum([ float(i["quantity"]) for i in cryptos_open ])
        # if cryptos_open != []:
        if sum_of_cryptos_open_quantity != 0:
            print()
            print("CRYPTO:")
            for i in cryptos_open:
                s = i["currency"]["code"] 
                a = float(i["quantity"])
                if a == 0: # skip if empty and not actually an open position
                    continue
                p = QUOTE_CRYPTO(s)
                p = find_price_in_open_listdict(s,ld["cod"]) if load_bool else QUOTE_CRYPTO(s) # p = QUOTE_CRYPTO(s)
                # print("DEBUG-C:",s,p)
                cryptos_dict[s].update_current(a,p)
                total_cryptos_open_amount += a
                total_cryptos_open_value += cryptos_dict[s].current_value
                cod.append({ "symbol": s, "quantity": a, "price": p, "value": cryptos_dict[s].current_value })
            if sort_alpha_bool:
                cod.sort(key=lambda x: x["symbol"], reverse=False)
            else:
                cod.sort(key=lambda x: float(x["value"]), reverse=False)
            for i in cod:
                s = i["symbol"]
                a = i["quantity"]
                p = i["price"]
                v = i["value"]
                print(f"* OPEN CRYPTO - {s} x{a} at ${D2(p)} each - est current value: ${D2(v)}")
            print(f"* TOTAL OPEN CRYPTO - {total_cryptos_open_amount} stocks for total ${D2(total_cryptos_open_value)} estimated value")
        # TODO: options open positions
        options_open = ld["options_open"] if load_bool else LOAD_OPEN_OPTIONS()
        if options_open != []:
            pass
        # show total open amounts
        if stocks_open != [] or cryptos_open != [] or options_open != []:
            total_open_amount = total_stocks_open_amount, total_cryptos_open_amount, total_options_open_amount
            total_open_value = total_stocks_open_value + total_cryptos_open_value + total_options_open_value
            print()
            print("TOTAL:")
            print(f"* total open positions value: ${D2(total_open_value)}")

        # quick inner function for profit printing
        def show_profits_from_orders_dictionary(dictionary, prefix=""):
            total_profit = 0
            total_amount = 0
            # get list of all symbols that are open
            stock_keys = [ i["symbol"] for i in sod ] if sod != [] else []
            crypto_keys = [ i["symbol"] for i in cod ] if cod != [] else []
            option_keys = [ i["symbol"] for i in ood ] if ood != [] else []
            all_keys = stock_keys + crypto_keys + option_keys
            list_dict = []
            # go thru each item in the dictionary which is a multi_order class and run latest_profit and latest_amount (not needed)        
            for sym,orders in dictionary.items():
                last_profit = orders.latest_profit()
                last_amount = orders.latest_amount() # <-- not needed as it fails when stocks split. open stocks make more senses
                ## open_string = " ** currently open **" if sym in all_keys else ""
                open_bool = True if sym in all_keys else False
                list_dict.append({"symbol":sym,"profit":last_profit,"open":open_bool})
                ## print(f"* {sym} net profit ${D2(last_profit)}"+open_string)
                total_profit += last_profit
                total_amount += last_amount
            # sort list by profit (previously we printed list above, and didn't this for loop because we didn't sort)
            if sort_alpha_bool:
                list_dict.sort(key=lambda x: x["symbol"], reverse=False) # increasing
            else:
                list_dict.sort(key=lambda x: float(x["profit"]), reverse=False) # increasing
            for i in list_dict:
                sym = i["symbol"]
                last_profit = i["profit"]
                open_string = " ** currently open **" if i["open"] else ""
                print(f"* {prefix}{sym} net profit ${D2(last_profit)}"+open_string)
            print(f"* {prefix}total net profit ${D2(total_profit)}")
            return (total_profit, total_amount, list_dict)

        # show each stocks profit
        print()
        print(f"--- Profits Based On Orders + Open Positions ---")
        print("* NOTE: For this profit approximation, we add up every symbols of the sell values, subtract the buy values, and if the symbol is open add in the current open value based of current ask price for the symbol")
        print("* NOTE: profit per stock = (current open position value) + (sum of all of the sells) - (sum of all of the buy orders)")
        total_stocks_profit, total_stocks_amount, total_cryptos_profit, total_cryptos_amount, total_options_profit, total_options_amount = 0,0,0,0,0,0
        list_dict_of_stock_profits, list_dict_of_crypto_profits, list_dict_of_option_profits = [], [], []
        profits_dict = {}
        if stock_orders != []:
            print()
            print(f"STOCKS:")
            total_stocks_profit, total_stocks_amount, list_dict_of_stock_profits = show_profits_from_orders_dictionary(stocks_dict,"STOCK ")
        if crypto_orders != []:
            print()
            print(f"CRYPTO:")
            total_cryptos_profit, total_cryptos_amount, list_dict_of_crypto_profits = show_profits_from_orders_dictionary(cryptos_dict, "CRYPTO ")
        if option_orders != []:
            print()
            print(f"OPTIONS:")
            total_options_profit, total_options_amount, list_dict_of_option_profits = show_profits_from_orders_dictionary(options_dict, "OPTION ")
        complete_profit = total_stocks_profit + total_cryptos_profit + total_options_profit
        print()
        print("TOTAL NET PROFIT:")
        print(f"* total net profit from stocks, crypto, and options: ${D2(complete_profit)}")
        print()

        # dividend profit
        print(f"--- Profits from Dividends ---")
        rs_divs_list = ld["dividends"] if load_bool else LOAD_DIVIDENDS()
        if rs_divs_list != [] or rs_divs_list is not None: # maybe just checking != [] is enough, doesn't hurt to check for None as well
            divs_list = []
            divs_sum = 0 # can also get divs sum with API: r.get_total_dividends()
            for i in rs_divs_list:
                symbol = URL2SYM(i["instrument"])
                amount_paid = float(i["amount"])
                date_string = i["paid_at"]
                state = i["state"]
                d = orders.dividend(symbol,amount_paid,date_string,state,run_date)
                divs_list.append(d)
                if state == "paid":
                    divs_sum += amount_paid

            # sort by value or alpha ---- but we will always sort by date
            # if sort_alpha_bool:
            #     sort(divs_list,key=lambda x: x.symbol_name)
            # else:
            #    sort(divs_list,key=lambda x: x.amount_paid)
            divs_list.sort(key=lambda x: x.date_epoch)
            for i in divs_list:
                print(f"* dividend from {i.symbol_name} on {i.date_nice()} for ${D2(i.payed_amount)} ({i.state})")
            print(f"TOTAL PAID DIVIDEND PROFIT: ${D2(divs_sum)}")
            print()

        print("--- Total Profit (Net Profit + Dividends) ---")
        complete_profit_plus_divs = complete_profit + divs_sum
        print(f"* total profit from stocks, crypto, and options + dividends: ${D2(complete_profit_plus_divs)}")
        print()

    ### TESTING
    # print(f"--- TESTING SOME VALUES ---")
    # sum_sells = 0
    # sum_buys = 0
    # sum_profits = 0
    # for sf in stocks_dict.values():
    #     a,b,c,d,e,f = sf.print_some_values() # prints and sets
    #     sum_sells += b
    #     sum_buys += c
    #     sum_profits += d
    # rat_pps = (sum_profits / sum_sells)*100
    # rat_ppb = (sum_profits / sum_buys)*100
    # print(f"** {sum_sells=} {sum_buys=} {sum_profits=} {rat_pps=} {rat_ppb=} **")
    # print()

    # print extra info footer
    print(f"--- Final Notes ---")

    # if profile info was saved to csv
    dir_full = get_save_dir()

    if info_type == "ALL" or info_type == "PROFILE":
        if csv_profile_bool:
            print(f"* saved profile data csvs to '{dir_full}' directory")

    if info_type == "PROFILE" and csv_profile_bool == False:
        print("* none")

    # if we loaded order data from api or dat.pkl file
    if info_type == "ALL" or info_type == "FINANCE":
        if load_bool:
            print(f"* loaded order data from '{FILENAME}' which ran on {run_date_orders}")
        else:
            print(f"* loaded order data from robinhood API run date {run_date_orders}")
    
    # save to order , open , and profit to csv
    if info_type == "ALL" or info_type == "FINANCE":
        if csv_bool:
            if stock_orders != []:
                print(f"* saving stock orders + open positions + net profits csvs to '{dir_full}' directory")
                print_all_stocks_to_csv(stock_orders)
                print_to_csv("All-Profits-Stocks",list_dict_of_stock_profits)
                if sod != []:
                    print_to_csv("All-Open-Stocks",sod)
                print(f"* saved stock csvs")
            if crypto_orders != []:
                print(f"* saving crypto orders + open positions + net profits csvs to '{dir_full}' directory")
                print_all_crypto_to_csv(crypto_orders)
                print_to_csv("All-Profits-Crypto",list_dict_of_crypto_profits)
                if cod != []:
                    print_to_csv("All-Open-Crypto",cod)
                print(f"* saved crypto csvs")
            if option_orders != []:
                print(f"* saving option orders + open positions + net profits csvs to '{dir_full}' directory")
                print_all_options_to_csv(option_orders)
                print_to_csv("All-Profits-Options",list_dict_of_option_profits)
                if ood != []:
                    print_to_csv("All-Open-Options",ood)
                print(f"* saved option csvs")
            if rs_divs_list != []:
                print(f"* saving dividends csv to '{dir_full}'")
                print_to_csv("All-Dividends",rs_divs_list)
    
        # Save api data to pickle file dat.pkl so we can use --load in future to load faster (but of course then its not live data)
        if save_bool:
            save_data(FILENAME, so = stock_orders, co = crypto_orders, oo = option_orders, sd = stocks_dict, cd = cryptos_dict, od = options_dict, soo = stocks_open, coo = cryptos_open, ooo = options_open, sod = sod, cod = cod, ood = ood, divs = rs_divs_list, verify_bool = True)

###################
####### MAIN ######
###################

def main():

    # these global variable's can be edited here
    global CREDENTIALSFILE, FILENAME, dir_suffix, cryptopairs

    # args parser

    arg_desc = f"rhood v{Version} - Text analysis of robinhood profile, portfolio and profits. Please review README.md for login instructions. There are 2 methods: creating '{CREDENTIALSFILE}' file (more secure), or providing credentials in the command line (less secure)."
    end_message = f"Example: first create '{CREDENTIALSFILE}' credentials file following the README.md instructions, then run # python rhood.py --all-info"
    parser = argparse.ArgumentParser(description=arg_desc,epilog=end_message)
    parser.add_argument("--username","-U",help="Robinhood username. Must be used with --password and --authkey, if 2 factor authentication is used.", action="store", default="")
    parser.add_argument("--password","-P",help="Robinhood password.", action="store", default="")
    parser.add_argument("--authkey","-K",help="2 factor authentication key. Only needed if 2Factor is enabled.", action="store", default="")
    parser.add_argument("--insecure","-I",help=f"Not recommended. Login insecurely without 2factor authentication. '{CREDENTIALSFILE}' only holds username line and password line in encoded base64 ascii format. Sidenote: default secure mode also needs third auth key line encoded as well.", action="store_true")
    parser.add_argument("--creds-file","-C",help=f"Where to load base64 encoded credentials from (README.md for more information). By default it is '{CREDENTIALSFILE}'.", action="store", default=CREDENTIALSFILE)
    parser.add_argument("--all-info","-i",help="Get all profile + order + open positions + profit info.",action="store_true")
    parser.add_argument("--profile-info","-r",help="Get only profile information.",action="store_true")
    parser.add_argument("--finance-info","-f",help="Get financial information: all orders + open positions + profit info.",action="store_true")
    parser.add_argument("--save","-s",help=f"Save all orders + open positions to file '{FILENAME}'. Only works with --all-info or --finance-info.",action="store_true")
    parser.add_argument("--load","-l",help=f"Load all orders + open positions from file '{FILENAME}', therefore we don't have to contact API; Saves time but gets older data. Only works  with --all-info or --finance-info.",action="store_true")
    parser.add_argument("--finance-file","-F",help=f"Change financial orders file to save to or load from. By default it is '{FILENAME}'.", action="store", default=FILENAME)
    parser.add_argument("--extra","-e",help="Shows extra order information (time consuming). only works with --all-info or --finance-info.",action="store_true")
    parser.add_argument("--csv","-c",help="Save all loaded orders to csv files in 'csv' directory (dir is created if missing). Only works  with --all-info or --finance-info.", action="store_true")
    parser.add_argument("--profile-csv","-p",help="Save all profile data to csv. Only works if --profile-info or --all-info used as well.", action="store_true")
    parser.add_argument("--csv-dir","-D",help=f"Change output directory for csv files generated by --csv and --profile-csv option, by default the directory is named '{dir_suffix}'.", action="store", default=dir_suffix)
    parser.add_argument("--sort-by-name","-S",help="Sorts open positions + profits by name instead of value. Only works if --finance-info or --all-info is used as well.", action="store_true")

    args = parser.parse_args()

    # parse save and load
    save_bool = args.save
    load_bool = args.load

    # extra information
    extra_info_bool = args.extra

    # save csv of orders
    csv_bool = args.csv
    csv_profile_bool = args.profile_csv

    # info bools
    all_info_bool = args.all_info
    profile_info_bool = args.profile_info
    finance_info_bool = args.finance_info
    if profile_info_bool and finance_info_bool:
        # if we are asking for profile + order info then just get all of it
        all_info_bool = True

    # sort type
    sort_alpha_bool = args.sort_by_name

    # credentials at cli, if not used the are "", we check for missing items inside LOGIN files
    cli_user = args.username
    cli_pass = args.password
    cli_key = args.authkey

    # error checking on saving and loading
    if load_bool and save_bool:
        print()
        print("* ERROR: Can't save and load. Try again with either save or load.")
        print()
        sys.exit(1)

    # Credentials file (if we don't need it, that is okay and handled in LOGIN functions)
    CREDENTIALSFILE = args.creds_file

    # Pickle file
    FILENAME = args.finance_file

    # csv directory
    dir_suffix = args.csv_dir

    # LOGIN securely or insecurely
    if not args.insecure:
        _login_output = LOGIN(un=cli_user,pw=cli_pass,ke=cli_key) # gives us r from secure login
    else:
        _login_output = LOGIN_INSECURE(un=cli_user,pw=cli_pass) # gives us r from insecure login

    # GET CRYPTOPAIRS (global var used in pairing crypto ids to coin name)
    cryptopairs = r.get_crypto_currency_pairs() # global var

    # kicking off main operation below:
    if all_info_bool: # this should be all info - get main profile & orders
        PRINT_ALL_PROFILE_AND_ORDERS(save_bool=save_bool, load_bool=load_bool, extra_info_bool=extra_info_bool,csv_bool=csv_bool,csv_profile_bool=csv_profile_bool,info_type="ALL", sort_alpha_bool=sort_alpha_bool)
    elif profile_info_bool: # this should be just profile info
        PRINT_ALL_PROFILE_AND_ORDERS(save_bool=save_bool, load_bool=load_bool, extra_info_bool=extra_info_bool,csv_bool=csv_bool,csv_profile_bool=csv_profile_bool,info_type="PROFILE", sort_alpha_bool=sort_alpha_bool)
    elif finance_info_bool: # this is just finance info
        PRINT_ALL_PROFILE_AND_ORDERS(save_bool=save_bool, load_bool=load_bool, extra_info_bool=extra_info_bool,csv_bool=csv_bool,csv_profile_bool=csv_profile_bool,info_type="FINANCE", sort_alpha_bool=sort_alpha_bool)

# Mains your Name!

if __name__ == "__main__":

    main()

# EOF
