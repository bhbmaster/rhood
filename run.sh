#!/bin/bash
# run rhood script and save its output & generate csvs. also save the orders to dat.pkl.
# make a dated copy into archives dir as well
DATE=$(/bin/date +%Y-%m-%d-%H%M)
mkdir archive 2> /dev/null
mkdir archive/output 2> /dev/null
mkdir archive/dat 2> /dev/null
# more info:
python rhood.py --all-info --extra --save --csv --profile-csv > output.txt 2>&1
# less info:
# python rhood.py --finance-info --extra --save --csv > output.txt 2>&1
/bin/cp "output.txt" "archive/output/output-$DATE.txt"
/bin/cp "dat.pkl" "archive/dat/dat-$DATE.pkl"
