#!/bin/bash

# === PURPOSE: ===
# run rhood script and save its output & generate csvs. also save the orders to dat.pkl.
# make a dated copy into archives dir as well. its purpose was to be run on a scheduled task via crontab or Windows scheduler.
# === HOW TO USE: ===
# make sure there is a "cred-encoded" file for authentication.
# see README.md for information on how to set that up.
# if you use none MFA robinhood this might work
# if you use MFA, this will not work as you need to put in the MFA (multi-factor authentication) key manually in.
# rhood used to work with MFA without manual intervention of putting in MFA, but stopped - something needs to be updated
#  ^-- TODO that I wont get around to anytime soon
# also update the PYTHON variable to match your python executable name that has all of the rhood requirements

DATE=$(date +%Y-%m-%d-%H%M)
# PYTHON="/cygdrive/c/Users/Admin/AppData/Local/Programs/Python/Python310/python.exe"
PYTHON=python3.11

mkdir archive 2> /dev/null
mkdir archive/output 2> /dev/null
mkdir archive/dat 2> /dev/null

# more info:
$PYTHON rhood.py --all-info --extra --save --csv --profile-csv > output.txt 2>&1
# less info:
# python rhood.py --finance-info --extra --save --csv > output.txt 2>&1

cp "output.txt" "archive/output/output-$DATE.txt"
cp "dat.pkl" "archive/dat/dat-$DATE.pkl"

# EOF