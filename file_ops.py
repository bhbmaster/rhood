import os
# import json
import pickle
import csv
from rhood import URL2SYM, ID2SYM

# save time consuming data to file
# sod, cod, ood = list of dict of open positions { "symbol", "quantity", "price",  "value" }
def save_data(filename,so,co,oo,sd,cd,od,soo,coo,ooo,sod,cod,ood,divs,run_date,loaded_username,verify_bool=False):
    save_data = { "run_date": run_date, "username": loaded_username, "stock_orders":so, "crypto_orders":co, "option_orders":oo, "stocks_dict":sd, "cryptos_dict":cd, "options_dict":od, "stocks_open":soo, "cryptos_open":coo, "options_open":ooo, "sod":sod, "cod":cod, "ood": ood, "dividends":divs }  # loaded_username is global <-- not anymore after refactor, have to bring it in via arg
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
        errext(2, f"Can't load {filename}, it is missing. Try running with --save parameter instead so that we contact the API for the order information and save the data to {filename}.")
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
    # if we didn't find symbol we will be here and that can only happen if corruption of file
    errext(2, "Loaded file might be corrupted as its missing price for {symbol}. Can't proceed further. Try again without loading.")

###################

# csv functions
def get_save_dir(run_date_orders, dir_suffix, user_string):
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
def print_to_csv(fname, toCSV, run_date_orders, dir_suffix, user_string):
    # create dir and get filename
    dir_full = get_save_dir(run_date_orders,dir_suffix, user_string)
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
def print_all_stocks_to_csv(RS_orders_all_stocks,run_date_orders,dir_suffix,user_string):
    # stocks are IDed by their instrument, get all of the unique instruments with a set
    instruments = set()
    for o in RS_orders_all_stocks:
        instruments.add(o["instrument"])
    # go thru each symbol and make csv
    for i in instruments:
        symbol = URL2SYM(i)
        current_orders = [ j for j in RS_orders_all_stocks if j["instrument"]==i ]
        print_to_csv("S-"+symbol,current_orders,run_date_orders,dir_suffix,user_string)
    # print all stocks (for fun)
    print_to_csv("S-(all)",RS_orders_all_stocks,run_date_orders,dir_suffix,user_string)

# print all crypto orders csvs
def print_all_crypto_to_csv(RS_orders_all_cryptos,run_date_orders,dir_suffix,user_string,cryptopairs):
    # crypto are IDed by their currency_pair_id, get all of the unique ones with a set
    currency_pair_ids = set()
    for o in RS_orders_all_cryptos:
        currency_pair_ids.add(o["currency_pair_id"])
    # go thru each symbol and make csv
    for i in currency_pair_ids:
        symbol = ID2SYM(i,cryptopairs)
        current_orders  = [ j for j in RS_orders_all_cryptos if j["currency_pair_id"]==i ]
        print_to_csv("C-"+symbol,current_orders,run_date_orders,dir_suffix,user_string)
    # print all stocks (for fun)
    print_to_csv("C-(all)",RS_orders_all_cryptos,run_date_orders,dir_suffix,user_string)


# print all options orders csvs - TODO: create + test when we get options. remember to prefix with "O" for options
def print_all_options_to_csv(RS_orders_all_options,run_date_orders,dir_suffix,user_string):
    pass