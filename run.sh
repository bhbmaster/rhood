#!/bin/bash
# run rhood script and save its output & generate csvs. also save the orders to dat.pkl.
# make a dated copy into archives dir as well
DATE=$(/bin/date +%Y-%m-%d-%H%M)
mkdir archive 2> /dev/null
# more info:
python rhood.py --all-info --extra --save --csv --profile-csv > output.txt
# less info:
# python rhood.py --finance-info --extra --save --csv > output.txt
/bin/cp "output.txt" "archive/output-$DATE.txt"
/bin/cp "dat.pkl" "archive/dat-$DATE.pkl"