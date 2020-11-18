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

# CONVERT MONEY STRING TO 2 DECIMAL 
def TOMONEY(string):
	if string is None:
		return "None"
	else:
		return f"{float(string):.2f}"


# PRINT STOCK ORDERS OF A SYMBOL OR ALL
def PRINT_STOCK_ORDERS(symbol=None):
    if symbol:
        func=r.orders.find_stock_orders(symbol=symbol)
    else:
        func=r.orders.find_stock_orders()
    print("\n".join([ f'{o["last_transaction_at"]} - {o["id"]} - {o["side"]}\tx{o["quantity"]}\t{URL2SYM(o["instrument"])} [{o["state"]}]\tavg: ${TOMONEY(o["average_price"])}\texec0/{len(o["executions"])}: ${TOMONEY(o["executions"][0]["price"])}\tprice: ${TOMONEY(o["price"])}' for o in func ]))

# PRINT CRYPTO ORDER OF A SYMBOL OR ALL
# MISSING FROM robin_stocks

# PRINT OPTIONS ORDER OF A SYMBOL OR ALL
# MISSING FROM robin_stocks

### MAIN ###

# currently want to run this part of the code if imported + not imported
LOGIN() # gives us r

if __name__ == "__main__":

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
    extended_hours_equity = profileData['extended_hours_equity']
    totalGainMinusDividends = equity - dividends - money_invested # missing cash_account_debits + 
    percentGain = totalGainMinusDividends/money_invested*100

    print(f"* Reported Deposits: {TOMONEY(deposits)}")
    print(f"* Reported Withdrawals: {TOMONEY(withdrawals)}")
    print(f"* Reported Debits: {TOMONEY(debits)}")
    print(f"* Reported Reversal Fees: {TOMONEY(reversal_fees)}")
    print(f"* The total money invested is {TOMONEY(money_invested)}")
    print(f"* The total equity is {TOMONEY(equity)}")
    print(f"* Sidenote: extended_hours_equity is {TOMONEY(extended_hours_equity)}") # added by me
    print(f"* The net worth has increased {percentDividend:.3f}% due to dividends that amount to {TOMONEY(dividends)}")
    print(f"* The net worth has increased {TOMONEY(percentGain)}% due to other gains that amount to {TOMONEY(totalGainMinusDividends)}")
    print()

    # print all stock orders (buy and sell)
    print(f"--- All Orders - Date: {datetime.datetime.now()} ---")
    PRINT_STOCK_ORDERS()
    print()

# EOF
