import robin_stocks as r
import pyotp
import sys
import json
import base64
import datetime

# TO IMPLEMENT unsync FOR FAST

### FUNCTIONS ###

# LOGIN
def LOGIN():
    global r
    # AUTH + LOGIN - LESS SECURE 
    # clear text "creds" file - 3 lines: email/username , password, authkey
    # with open('creds') as f:
    #     lines = f.readlines()

    # AUTH + LOGIN - MORE SECURE
    # more secure "creds-encoded" - we use base64 encoding (so anyone looking over your shoulder can't see your UN,PW,KEY)
    # create by first writing cleartext "creds" file
    # then run this in bash                       # python -c 'import base64; print(base64.b64encode(open("creds","r").read().encode("utf-8")).decode("utf-8"))' > creds-encoded
    # confirm you see base64 alphanumerics here   # cat creds-encoded
    # try to revert back                          # python -c 'import base64; print(base64.b64decode(open("creds-encoded","r").read()).decode("utf-8"))'
    # if you see the email/username , password, authkey lines in that order then you can delete the "creds" file with: # rm creds
    with open("creds-encoded") as f:
        lines = base64.b64decode(f.read()).decode("utf-8").split()

    EMAIL, PASSWD, KEY = map(lambda x: x.strip(), lines)

    ptot = pyotp.TOTP(KEY)
    ptot_now = ptot.now()

    login = r.login(EMAIL,PASSWD,mfa_code=ptot_now)
    return login

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

# SIMPLE CONVERT INSTRUMENT URL TO SYMBOL
def URL2SYM(url):
    return r.get_symbol_by_url(url)


# PRINT STOCK ORDERS OF A SYMBOL OR ALL
def PRINT_STOCK_ORDERS(symbol=None):
    if symbol:
        func=r.orders.find_stock_orders(symbol=symbol)
    else:
        func=r.orders.find_stock_orders()
    print("\n".join([ f'{o["last_transaction_at"]} - {o["id"]} - {o["side"]}\tx{o["quantity"]}\t{URL2SYM(o["instrument"])} [{o["state"]}]\tavg: ${o["average_price"]:.2f}\texec0/{len(o["executions"])}: ${o["executions"][0]["price"]:.2f}\tprice: ${o["price"]:.2f}' for o in func ]))

# PRINT CRYPTO ORDER OF A SYMBOL OR ALL
# MISSING FROM robin_stocks

# PRINT OPTIONS ORDER OF A SYMBOL OR ALL
# MISSING FROM robin_stocks

### MAIN ###

# currently want to run this part of the code if imported + not imported
LOGIN() # gives us r

if __name__ == "__main__":

    prof_type = ["account","basic","investment","portfolio","security","user"]

    for prof in prof_type:
        print(f"---{prof} Profile---")
        prof_func = getattr(r.profiles,f"load_{prof}_profile")
        print("\n".join([ f"* {i[0]}: {i[1]}" for i in prof_func().items() ]))
        print()

    print(f"--- All Orders - Date: {datetime.datetime.now()} ---")
    PRINT_STOCK_ORDERS()
    print()

# EOF
