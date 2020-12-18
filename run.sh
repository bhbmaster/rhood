#!/bin/bash
# run rhood script and save its output & generate csvs. also save the orders to dat.pkl.
# make a dated copy into archives dir as well
DATE=$(/bin/date +%Y-%m-%d-%H%M)
mkdir archive 2> /dev/null
python rhood.py --all-info --extra --save --csv --profile-csv > output.txt  # this also generates dat.pkl
/bin/cp "output.txt" "archive/output-$DATE.txt"
/bin/cp "dat.pkl" "archive/dat-$DATE.pkl"