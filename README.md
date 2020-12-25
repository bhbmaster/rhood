# RHOOD - Robinhood Stocks Analysis

Rhood provides a text analysis of your robinhood portfolio. It provides all of the profile data, order data, open positions, net profits, dividends, and total profits.

Rhood provides an excellent way to see your profit for each symbol ever held. Robinhood webapp & native application doesn't provide this information (at least I couldn't find it). You can see your total revenue, and you can see symbols total return. However, robinhood's total return per symbol, seems to clear out if you sell the whole symbol; or maybe part sell of the symbol distorts it too - I am not sure. My application, rhood, tells you the total return of each stock regardless of sales. This gives you a good idea as to which stocks, crypto or option* were your most advantageous (and least advantageous).

As this generates very private data, the output should be viewed with discretely.

Example output which is made up but shows general concept:

```
...many lines cut off for brevity (cut lines might have shown all profile info, all orders and open positions)...

STOCKS:
* STOCK CBAT net profit $-3.73
* STOCK MGM net profit $27.25 ** currently open **
* STOCK NCLH net profit $11.66 ** currently open **
* STOCK SPCE net profit $169.44
* STOCK total net profit $204.62

CRYPTO:
* CRYPTO ETH net profit $-3.31
* CRYPTO BTC net profit $67.34 ** currently open **
* CRYPTO total net profit $64.03

TOTAL NET PROFIT:
* total net profit from stocks, crypto, and options: $268.65

--- Profits from Dividends ---
* dividend from SPXL on 2020-07-01 11:18:12 +0000 for $0.19 (paid)
* dividend from AAPL on 2020-08-14 13:18:03 +0000 for $0.60 (paid)
TOTAL DIVIDEND PAY: $0.79

TOTAL PROFIT (NET PROFIT + DIVIDENDS):
* total profit from stocks, crypto, and options + dividends: $269.44
```

**Requirements:** python3.9 + pip install robin_stocks and pyotp

**Robinhood API used:** https://github.com/jmfernandes/robin_stocks

The tested versions are python3.9 and the modules listed in requirements.txt (along with the tested versions).

## WORK IN PROGRESS

* See todo list at the bottom. Options are not taken into account, yet.

## SHELL QUICK START GUIDE

Here is a quick start guide for shell users:

```
# install rhood

git clone https://github.com/bhbmaster/rhood
cd rhood

# install its dependencies

pip install -r requirements.txt

# run rhood using method A or method B:

# method A -- if you do not have 2 factor authentication enabled run this:

python rhood.py --all-info --username 'your@email.com' --password 'YOURPASSWORD' --insecure

# method B -- if you have 2 factor authentication and your authentication key (its an alphanumeric code provided only once at the beginning of your 2 factor authentication setup)

python rhood.py --all-info --username 'your@email.com' --password 'YOURPASSWORD' --authkey 'YOUR2FACTORCODE'
```

**SIDENOTE 1:** The 2 factor authentication key 'YOUR2FACTORCODE' is not the 6 digit code you get every time you want to login. Instead its an alphanumeric code presented at the beginning of setting up your 2 factor. IT looks like this 'TZIJ9PPENAA2X69Z' (this is not anyones code. I changed the characters.)

**SIDENOTE 2:** It is called --insecure, for the purposes of labeling my code. I labelled none 2 factor authentication as "insecure" and 2 factor auth as "secure". The actual login for both methods is still done over API and your credentials are not saved anywhere, so both are actually secure methods.

**SIDENOTE 3:** If rhood is going to be ran often or in a script, I recommend using a 'creds-encoded' file instead of supplying your credentials in the CLI. More information on cred files and all of the login methods are described below.

## HOW TO USE RHOOD

First select a login method, preferably more secure ones. Then select the arguments you want to use. Most likely --all-info to start off, that just give - all the info (all profile info, all orders, open positions, net profits, dividends, and total profits)

## LOGIN METHODS

There are 4 methods of login in. In order from least to most secure:

1. secure login using base64 encoded file 'creds-encoded' that has username/email on first line and password on second line and authkey on third line (pre-encoding)
1. insecure login using base64 encoded file 'creds-encoded' that has username/email on first line and password on second line (pre-encoding)
1. secure login with CLI using --username --password and --authkey
1. insecure login with CLI --username and --password

secure vs insecure simply means, secure is your account has 2 factor authentication mode, where as insecure means your account does not have 2 factor authentication.

## LOGIN METHOD 1 ) LOGIN SECURELY - USE AUTHENTICATION KEY AND CREATE CREDS FILE

For this to work, I encourage to use 2 factor authentication. Please set it up. I installed the Google Authenticator app on my phone and then I enabled 2 factor from Robinhood app the "authentication with an app" 2 factor method (not the SMS method).

More instructions: https://robinhood.com/us/en/support/articles/twofactor-authentication/

You will be given an alphanumetic API key that looks like this "TZIJ9PPENAA2X69Z". You will use it to create the credentials file below.

**NOTE:** I am not sure if the 2 factor with SMS method works, it might. If it doesn't then just switch to 2 factor with an app

###  CREATE ENCODED CREDS FILE

Before we can do any work, first create a credentials files called 'creds-encoded'.

Its an encoded file of your email, password, and API key. We start with a clear text credentials file 'creds', but then we convert it to be encoded for extra security.

**NOTE:** Although, having an encoded credentials file provides an extra level of security so that your creds are not stored in clear text on your PC, please take extra caution your computer is secured other methods (perhaps accessing via 2 factor as well)

Steps to create the encoded credentials file:

1. Create a clear text 'creds' file which has 3 lines: UN, PW, and KEY. For me it looked like this:

```
bhbmaster@gmail.com
PineapplesExpress
TZIJ9PPENAA2X69Z
```

1. Encode it with this python or bash command.

```
# python command
python -c 'import base64; print(base64.b64encode(open("creds","r").read().encode("utf-8")).decode("utf-8"))' > creds-encoded

# bash command
cat creds | base64 > creds-encoded
```

1. Verify you see an encoded file

```
cat creds-encoded
```

1. Verify the file decodes correctly. You should see your UN, PW, and KEY.

```
# python command
python -c 'import base64; print(base64.b64decode(open("creds-encoded","r").read()).decode("utf-8"))'

# bash command
cat creds-encoded | base64 -d 2> /dev/null
```

Example output (modified for privacy):

```
PPhib3453455QGdtYWlsasERTVCXYWlyMTIz123412341230VlZFTkJLMlg0N1A=
```

1. If you see the original output, then delete the original file. The software will use the creds-encoded file to load your credentials by decoding it correctly.

```
rm creds
```

## LOGIN METHOD 2 ) LOGIN INSECURELY WITH CREDENTIALS FILE - NOT RECOMMENDED

One can login with username and password as well - without 2 factor authentication. It is not recommended, but it works.

Follow the instructions above to create a creds-encoded file with just username and password, missing the auth key.

So it would look like this pre encoding:

```
bhbmaster@gmail.com
PineapplesExpress
```

Then include the the --insecure (or -I) argument in all of your rhood.py commands.

## LOGIN METHOD 3 and 4 ) USING CLI TO LOGIN

If you have 2 factor authentication, you would use secure login with CLI like so:

```
# syntax:
python rhood.py --username bhbmaster@gmail.com --password PineapplesExpress --authkey TZIJ9PPENAA2X69Z [rest of the options]
# example:
python rhood.py --username bhbmaster@gmail.com --password PineapplesExpress --authkey TZIJ9PPENAA2X69Z --all-info
```

If you have 2 factor authentication disabled, you would use insecure login with CLI like so:

```
# syntax:
python rhood.py --username bhbmaster@gmail.com --password PineapplesExpress [rest of the options]
# example:
python rhood.py --username bhbmaster@gmail.com --password PineapplesExpress --all-info
```

**SIDENOTE:** instead of using --username, --password, and --authkey which are 'wordy', you can use -U, -P and -A respectivly.

## PRINT ALL INFORMATION

Add the --all-info argument to rhood (-i for short) to print all profile information (lots of sensitive information), order information (Stock, Crypto, Option), open positions, net profits (see note below), dividends, and total profits.

```
python rhood.py --all-info
```

**NOTE:** To get any information out of rhood, you must at least use --all-info. Without it, its only useful to be played with interactively (see Playground).

**NOTE OF PROFIT CALCULATION:** Net Profits are calculated by subtracting the sum of the buy from the sells, then adding the open positions value. The open position values are calculated by multiplying current help quantity by the current ask_price (which is always changing). Therefore, if a stock, crypto or option is open then we are only getting an estimate of the profit by assuming we also sell the entire stock right now. If a symbol is currently closed (no quantity is held), then open position value can be ignored as its just 0. The term symbol refers to stocks, crypto coins, and options. Then dividend profit is calculated by summing all paid dividends. Total profit is the sum of dividend profits and net profits.

```
Net Profit For Symbol = (Sum of filled Sells) - (Sum of filled Buys) + (Open Position Value)
Dividends = (Sum of all paid dividends)
Total Profit = (Sum of all Net Profits from all symbols) + (Dividends)
```

## ONLY GETTING PROFILE INFORMATION OR FINANCIAL INFORMATION

Getting all of the information might not be the intent. So other then using a bunch of grep and regex on the final output to get the desired info. You can specify if you want just the profile information (--profile-info), or financial information (--finance-info).

Profile information includes only profile data. This switch can be used with --profile-csv. Other switches that rely on --finance-info will just be ignored (no errors shown)

```
python rhood.py --profile-info
```

Finance info includes only financial data (order information, open positions, net profits, dividends, and total profits). This switch can be used with --csv, --load, --save, --extra. Other switches that rely on --profile-info, will be ignored.

```
python rhood.py --finance-info
```

If both profile-info and finance-info switches are used, then its equivalent of just using --all-info. This way all switches work, --save, --load, --extra, --csv, --profile-csv.

```
python rhood.py --finance-info --profile-info  # both of these lines return the same output
python rhood.py --all-info                     # both of these lines return the same output
```

**SIDENOTE:** The old --info switch was renamed to --all-info

## SAVING AND LOADING STOCK ORDER INFORMATION

Checking the API for all of the orders is time consuming. Try to save the data locally & loading it. Of course if any orders were done since then, we will not have the most up to date information. Its always saved and load to 'dat.pkl' file. You can save a copy if you need, and if you need to use an older copy just rename or overwrite it to dat.pkl.

Save order information to dat.pkl:

```
python rhood.py --all-info --save
```

Load order information from dat.pkl:

```
python rhood.py --all-info --load
```

Sidenote: saving and loading only makes sense if you also use --all-info/-i option 
Sidenote: -s is short for --save, -l is short for --load

## GENERATE CSVs

The --csv or -c option save all of the stock, crypto and options orders + open positions + profits + dividends into CSV files. It saves the data as its recieved from the API. This can be loaded from saved orders (with --load option) file or directly from API (with out --load option).

```
python rhood.py --all-info --csv
```

To save all profile data use the --profile-csv switch

```
python rhood.py --all-info --profile-csv         # save profile info to csvs
python rhood.py --all-info --profile-csv --csv   # save profile info & stock orders + open positions + profits + dividends to csv 
```

## EXTRA INFORMATION ABOUT ORDERS

To view all of the information returned from the robinhood API about every order run it with --extra option or --csv option (csv saves the same information). This extra information is omitted during normal operations as we are only concerned with each orders: date, price, amount, state.

```
python rhood.py --all-info --extra              # Can use extra when all info is shown.
python rhood.py --finance-info --extra          # Or can use extra with finance-info (it won't do anything with profile-info).
python rhood.py --all-info --extra --load       # Can also load saved orders to lower API time. Works with all-info.
python rhood.py --finance-info --extra --load   # Can also load saved orders to lower API time. Works with finance-info.

```

This option can be ran with --save and --load. Even though load offers speed increases by avoiding contacting the API for order parsing, this option will still be a little time consuming as contact the API to map IDs to Symbol names.

## PARSING WITH GREP FOR A SPECIFIC SYMBOL

Here is how to get information about a specific symbol you have traded (stock or crypto).

First generate the all of the financial information by running one of the three commands below (just run one; they all return equally important data for the current purpose):

```
python rhood.py --all-info --extra --save --csv > output.txt
tpython rhood.py --finance-info --extra --save --csv > output.txt
./run.sh                             # this also generates an output.txt
```

Then grep the output for your stock:

```
cat output.txt | grep TSLA
```

**SIDENOTE:** grep is a linux/unix/mac program that searches for strings that match a specific regular expression (search string). In other words for the example above, this shows me only the lines that have the word TSLA in them. Windows users can also get grep if they utilize some sort of linux emulator such as cygwin, or windows 10's bash ability.

The above command has the following output for a random user:

```
2020-07-13T18:15:55.663576Z - a1053cf0-abcde-4910-9e04-abcde - buy        x0.06341400     TSLA [S|filled] avg: $1576.94   exec1/2: 
$1574.70        price: $1654.93
...lines skipped for brevity...
2020-12-09T15:53:58.910000Z - bc4c8aed-abcde-46dd-8106-abcde - buy        x2.00000000     TSLA [S|filled] avg: $639.68    exec1/1: 
$639.68 price: $671.58
2020-12-14T18:48:28.147000Z - 75985dd4-abcde-495a-adf3-abcde - buy        x1.00000000     TSLA [S|filled] avg: $637.19    exec1/1: 
$637.19 price: $669.10

...lines skiped for brevity...
* sym# 10/41 ord# 41/42 tot_ord# 156 - 2020-12-09 15:53:58 +0000 - TSLA - buy - x2.0 at $2.0000 - value $1279.36
* sym# 10/41 ord# 42/42 tot_ord# 157 - 2020-12-14 18:48:28 +0000 - TSLA - buy - x1.0 at $1.0000 - value $637.19

* OPEN STOCK - TSLA x3.0 at $634.13 each - est current value: $1902.38
* TSLA net profit $695.66 ** currently open **
```

**Sidenote:** Above information shows the order information as shown by the robinhood API, followed by the info as it was parsed by rhood.py (this is similar to the returned API order info, except it also shows the value), then it shows any open positions, finally it shows the net profits. From this data, we see there is a total of 42 orders with TSLA with 3 open stocks and profited $695 so far. Since this is an open stock, we will only see that full profit after selling all of TSLA at current ask price ($634.13). If TSLA paid dividends (they currently do not), then that profit would appear on here too.

## HELP

Run this to see all of the options.

```
python rhood.py --help
```

## SCHEDULING

You can run this script on repeat per a schedule (example daily) and analyze the results separately. For example grepping for "net profit" and then viewing how your net profit changes every day.

You can schedule the script to run in windows with Windows task scheduler that will run a bat file, that kicks off the run.sh shell script. For windows you need cygwin or another source of a bash.exe to get this running.

In Linux/MAC you can schedule run.sh to run on a crontask.

* run.sh --> this script runs rhood.py with extra information and saves output to a dated output file and a dated pickle file.
* run.bat --> not included but you can make it.

run.bat would have contents similar to this:

```
@echo off
c:
cd \path\to\your\rhood\
c:\path\to\your\bash.exe -c "cd /cygdrive/c/path/to/your/rhood; ./run.sh"
```

## EXTRA INFORMATION

* Only filled orders are taken into account. orders that were cancelled or are currently pending / queued do not take into account for order parsing, open positions, or profit calculations.

* Open positions and net profits are sorted from lowest value symbols to highest. you can use the --sort-name (-S) option to instead sort alphabetically by name.

* Only paid dividends are taken into account for total profit from dividends

* If --load option is used, the dat.pkl file contains the following information: username, run date & time, all of the stock, crypto and options orders (as received from API), and all of the stock, crypto and option open positions, and dividends.

## LIMITATIONS

* Credentials file must be named 'creds-encoded' and be present in current working directory.

* The --save option saves 'dat.pkl' into current working directory. --load can only load that file. Specifying other files is not possible.

* The --load option can only be used if 'dat.pkl' file is present in current working directory.

* The --load option only works if the username logging in matches the username saved in the 'dat.pkl' file.

* If dividend payment is pending, the pay date is estimated to current run date. Only consider pay dates of "paid" dividends.

## TODO

* Options are not yet included as I don't have any. Looking for any information regarding how the data structure or output look like for the APIs methods: option orders, and option open positions.

* If we use --load data from pickle file, then we should also use the ask_price of open positions at the loaded date, instead of the current date. otherwise the value will constantly change. this will give correct profits on that date. we could include option to evaluate loaded open positions with current ask price (--eval-loaded-current, -L), however, if stock splits occurred then we will be in a mathematics mess, that I don't want to deal with. <-- might need to check none robin_stocks API as this API doesn't have historical price ability (maybe it does, I just can't find it.

* Allow insecure credentials, without 2factor authentication. add --insecure / -I flag. due to 2 methods of login, we now have to remove interactive mode (it was useless anyways). **DONE, need to test.**

* Sort open positions & net profits alphabetically, or by value. default value, include option --sort-by-name / -S. **DONE**

* Add login for secure and insecure mode using CLI arguments, without needing 'creds-encoded' file. Will add --username (-U), --password (-P), --authkey (--K). **DONE**

* Code refactor: combine login secure and insecure into 1 login method.

* Add dividend profit to my calculations. **DONE**