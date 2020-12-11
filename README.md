# Robinhood Stocks Analysis

Text analysis of your robinhood portfolio. Absolutely everything you wanted to know. This generates very personal data, so make sure noone is standing around you.

Requirements: python3.9 + pip install robin_stocks and pyotp

The tested versions are python3.9 and what you see in requirements.txt for the modules.

## Work In Progress

Here is what needs work:

- Anything with options is not tested, because I do not have options
- Profit calculations are wrong
- So far useful to get all stock transations into CSVs:

    python rhood.py --info --csv

## Create Encoded Permissions File

Before we can do any work, first create a creds-encoded file. Its an encoded file of your email, password, and API key.

Steps to create encoded file:

(1) Create a clear text "creds" file which has 3 lines: UN, PW, and KEY.

    email/username
    password
    authkey

(2) Encode it with this bash command.

    python -c 'import base64; print(base64.b64encode(open("creds","r").read().encode("utf-8")).decode("utf-8"))' > creds-encoded

(3) Verify you see an encoded file

    cat creds-encoded

(4) Verify the file decodes correctly. You should see your UN, PW, and KEY.

    python -c 'import base64; print(base64.b64decode(open("creds-encoded","r").read()).decode("utf-8"))'

(5) If you see the original output, then delete the original file. The software will use the creds-encoded file to load your credentials by decodeing it correctly.

    rm creds

## Print All Information

Then to print all profile information (lots of sensitive information) + order information (Stock, Crypto, Option) - add the info argument to rhood (-i or --info). Use python or ipython. Personally I prefer ipython as it has better usability:

    python rhood.py --info
    python -i rhood.py --info

## Saving and Loading Stock Order Information

Checking the API for all of the orders is time consuming. Try to save the data locally & loading it. Of course if any orders were done since then, we will not have the most up to date information. Its always saved and load to 'dat.pkl' file. You can save a copy if you need, and if you need to use an older copy just rename or overwrite it to dat.pkl.

Save order information to dat.pkl:

    python rhood.py --info --save

Load order information from dat.pkl:

    python rhood.py --info --load

Sidenote: saving and loading only makes sense if you also use --info/-i option 
Sidenote: -s is short for --save, -l is short for --load

## Generate Order CSVs

The --csv or -c option save all of the stock, crypto and options orders into CSV files. It saves the data as its recieved from the API. This can be loaded from saved orders (with --load option) file or directly from API (with out --load option).

    python rhood.py --info --load --csv

## Extra information about orders

If you need to see alot of extra information about each order. This is alot of extra information, as during normal operations we only need the average price, amount, and date - well we also check to make sure the transaction state was not cancelled.

    python rhood.py --extra

This option can be ran with --save and --load. Even though load offers speed increases by avoiding contacting the API for order parsing, it will still be a little time consuming as during printing the extra information we will check with the API to map symbol IDs to their names.

## To view options help

Run this to see all of the options.

    python rhood.py --help

## Scheduling

You can run this script daily and analyze the results seperately. For example grepping for "net profit" and then viewing how your net profit changes every day.

You can schedule the script to run in windows with Windows task scheduler that will run a bat file, that kicks off the run.sh shell script. For windows you need cygwin or another source of a bash.exe to get this running.

In Linux/MAC you can schedule run.sh to run on a crontask.

* run.sh --> this script runs rhood.py with extra information and saves output to a dated output file and a dated pickle file.
* run.bat --> not included but you can make it.

run.bat would have contents similar to this:

    @echo off
    c:
    cd \path\to\your\rhood\
    c:\path\to\your\bash.exe -c "cd /cygdrive/c/path/to/your/rhood; ./run.sh"

## Playground

Want to mess with the objects by yourself?

Run either of these to enter python interactively and then mess with the robin_stocks r object (which has already loged you in). It will login for you and the rest is up to you:

    ipython -i rhood.py
    python -i rhood.py

Example:

     python -i rhood.py           # launch rhood with python or ipython in interactive mode
     > r.get_all_stock_orders()   # shows all stock orders information