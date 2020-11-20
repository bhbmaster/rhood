# Robinhood Stocks Analysis

**Unfinished**

Requirements: python3.9 + pip install robin_stocks

First create a creds-encoded file (follow instructions in the comments of rhood.py). Its an encoded file of your email, password, and API key.

Run either of these to enter python interactively and then mess with the robin_stocks r object (which has already loged you in):

    ipython -i rhood.py
    python -i rhood.py

Example:
     python -i rhood.py           # or ipython
     > r.get_all_stock_orders()   # shows all stock orders information

To print all profile information (lots of sensitive information) + order information (Stock, Crypto, Option) - run either of these with extra -i argument (stands for info):

    ipython rhood.py -i
    python rhood.py -i
    ipython -i rhood.py -i
    python -i rhood.py -i
