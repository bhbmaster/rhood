a# RHOOD - Robinhood Stocks Analysis

Rhood provides a text analysis of your robinhood portfolio. It provides all of the profile data, order data, open positions, and net profits.

Rhood provides an excellent way to see your profit per each symbol (stock, crypto and options*) that you ever owed. Robinhood webapp & native application doesn't provide this information (at least I couldn't find it). You can see your total revenue, and you can see symbols total return. However, robinhoods total return per symbol, seems to clear out if you sell the whole symbol; or maybe part sell of the symbol distorts it too - I am not sure. My application, rhood, tells you the total return of each stock regardless of sales. This gives you a good idea as to which stocks, crypto or option* were your most advantageous (and least advantageous).

As this generates very private data, the output should be viewed with discretely.

Requirements: python3.9 + pip install robin_stocks and pyotp

The tested versions are python3.9 and the modules listed in requirements.txt (along with the tested versions).

**NOTE*: Options are not actually included yet as they are a work in progress.

## WORK IN PROGRESS

Here is what needs work:

- Options are not calculated as I don't have any. I need to get some and then I can work them into the code. So if you are using only stocks + crypto or one or the other, then you this code will be useful.

## SECURITY ###

For this to work, I encourage to use 2 factor authentication. Please set it up. I installed the Google Authenticator app on my phone and then I enabled 2 factor from Robinhood app the "authentication with an app" 2 factor method (not the SMS method).

More instructions: https://robinhood.com/us/en/support/articles/twofactor-authentication/

You will be given an alphanumetic API key that looks like this "TZIJ9PPENAA2X69Z". You will use it to create the credentials file below.

**NOTE:** I am not sure if the 2 factor with SMS method works, it might. If it doesn't then just switch to 2 factor with an app

## CREATE ENCODED PERMISSIONS FILE

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

1. Encode it with this bash command.

```
python -c 'import base64; print(base64.b64encode(open("creds","r").read().encode("utf-8")).decode("utf-8"))' > creds-encoded
```

1. Verify you see an encoded file

```
cat creds-encoded
```

1. Verify the file decodes correctly. You should see your UN, PW, and KEY.

```
python -c 'import base64; print(base64.b64decode(open("creds-encoded","r").read()).decode("utf-8"))'
```

Example output (modified for privacy):

```
PPhib3453455QGdtYWlsasERTVCXYWlyMTIz123412341230VlZFTkJLMlg0N1A=
```

1. If you see the original output, then delete the original file. The software will use the creds-encoded file to load your credentials by decodeing it correctly.

```
rm creds
```

## PRINT ALL INFORMATION

Add the --all-info argument to rhood (-i for short) to print all profile information (lots of sensitive information), order information (Stock, Crypto, Option), open positions, and net profits (see note below).

```
python rhood.py --all-info
```

**NOTE:** To get any information out of rhood, you must at least use --all-info. Without it, its only useful to be played with interactively (see Playground).

**NOTE OF PROFIT CALCULATION:** Net Profits are calculated by subtracting the sum of the buy from the sells, then adding the open positions value. The open position values are calculated by multiplying current help quantity by the current ask_price. Therefore, if a stock, crypto or option is open then we are getting an estimate of the profit by assuming we also sell the entire stock right now. If a symbol is currently closed (no quantity is held), then open position value can be ignored as its just 0. The term symbol refers to stocks, crypto coins, and options.

```
Net Profit For Symbol = (Sum of Sells) - (Sum of Buys) + (Open Position Value)
Total Profit = (Sum of all Net Profits from all symbols)
```

## ONLY GETTING PROFILE INFORMATION OR FINANCIAL INFORMATION

Getting all of the information might not be the intent. So other then using a bunch of grep and regex on the final output to get the desired info. You can specify if you want just the profile information (--profile-info), or financial information (--finance-info).

Profile information includes only profile data. This switch can be used with --profile-csv. Other switches that rely on --finance-info will just be ignored (no errors shown)

```
python rhood.py --profile-info
```

Finance info includes only financial data (order information, open positions, and net profits). This switch can be used with --csv, --load, --save, --extra. Other switches that rely on --profile-info, will be ignored.

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

The --csv or -c option save all of the stock, crypto and options orders + open positions + profits into CSV files. It saves the data as its recieved from the API. This can be loaded from saved orders (with --load option) file or directly from API (with out --load option).

```
python rhood.py --all-info --csv
```

To save all profile data use the --profile-csv switch

```
python rhood.py --all-info --profile-csv         # save profile info to csvs
python rhood.py --all-info --profile-csv --csv   # save profile info & stock orders + open positions + profits to csv 
```

## EXTRA INFORMATION ABOUT ORDERS

To view all of the information returned from the robinhood API about every order run it with --extra option or --csv option (csv saves the same information). This extra information is ommited during normal operations as we are only concerned with each orders: date, price, amount, state.

```
python rhood.py --extra
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

**SIDENOTE:** grep is a linux/unix/mac program that searches for strings that match a specific regular expression (search string). In otherwords for the example above, this shows me only the lines that have the word TSLA in them. Windows users can also get grep if they utilize some sort of linux emulator such as cygwin, or windows 10's bash ability.

The above command has the following output for a random user:

```
2020-07-13T18:15:55.663576Z - a1053cf0-abcde-4910-9e04-abcde - buy        x0.06341400     TSLA [S|filled] avg: $1576.94   exec1/2: 
$1574.70        price: $1654.93
...skip...
2020-12-09T15:53:58.910000Z - bc4c8aed-abcde-46dd-8106-abcde - buy        x2.00000000     TSLA [S|filled] avg: $639.68    exec1/1: 
$639.68 price: $671.58
2020-12-14T18:48:28.147000Z - 75985dd4-abcde-495a-adf3-abcde - buy        x1.00000000     TSLA [S|filled] avg: $637.19    exec1/1: 
$637.19 price: $669.10

...skip...
* sym# 10/41 ord# 41/42 tot_ord# 156 - 2020-12-09 15:53:58 +0000 - TSLA - buy - x2.0 at $2.0000 - value $1279.36
* sym# 10/41 ord# 42/42 tot_ord# 157 - 2020-12-14 18:48:28 +0000 - TSLA - buy - x1.0 at $1.0000 - value $637.19

* OPEN STOCK - TSLA x3.0 at $634.13 each - est current value: $1902.38
* TSLA net profit $695.66 ** currently open **
```

**Sidenote:** the above information from top to bottom shows the order information as shown by the robinhood API, then the pertinent stock info as it was parsed by rhood.py (this is similar to the returned order info, except it also shows the value), then it shows any open positions, then my net profits. So this tells the used they had a total of 42 orders with TSLA and made 695$ off of it so far TSLA, and that they still currently have 3 shares of TSLA. Since this is an open stock, we will see that $695 profit only after selling TSLA right now at its current ask price ($634.13)

## HELP

Run this to see all of the options.

```
python rhood.py --help
```

## SCHEDULING

You can run this script on repeat per a schedule (example daily) and analyze the results seperately. For example grepping for "net profit" and then viewing how your net profit changes every day.

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

## INTERACTIVE PLAYGROUND

Want to mess with the objects by yourself?

Run either of these to enter python interactively and then mess with the robin_stocks r object (which has already loged you in). It will login for you and the rest is up to you:

```
ipython -i rhood.py
python -i rhood.py
```

Example:

```
python -i rhood.py               # launch rhood with python or ipython in interactive mode
> r.get_all_stock_orders()       # shows all stock orders information
> r.get_open_stock_positions()   # shows all currently open stocks
```