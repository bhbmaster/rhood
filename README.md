# Robinhood Stocks Analysis

Text analysis of your robinhood portfolio. Absolutely everything you wanted to know. This generates very personal data, so make sure noone is standing around you.

**-->Unfinished<--**

Requirements: python3.9 + pip install robin_stocks and pyotp

The tested versions are python3.9 and what you see in requirements.txt for the modules.

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

    python rhood.py -i
    python -i rhood.py -i

## Playground

Want to mess with the objects by yourself?

Run either of these to enter python interactively and then mess with the robin_stocks r object (which has already loged you in). It will login for you and the rest is up to you:

    ipython -i rhood.py
    python -i rhood.py

Example:

     python -i rhood.py           # launch rhood with python or ipython in interactive mode
     > r.get_all_stock_orders()   # shows all stock orders information