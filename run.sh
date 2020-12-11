#!/bin/bash
# run rhood script and save its output. also save the orders to dat.pkl.
# make a dated copy into archives dir as well
DATE=$(/bin/date +%Y-%m-%d-%H%M)
mkdir archive 2> /dev/null
python rhood.py --info --extra --save > "archive/output-$DATE-extra"  # this also generates dat.pkl
/bin/cp "dat.pkl" "archive/dat-$DATE.pkl"