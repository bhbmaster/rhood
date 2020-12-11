#!/bin/bash
# run rhood script and output is saved to a dated file + dated dat-DATE.pkl file.
DATE=$(/bin/date +%Y-%m-%d-%H%M)
python rhood.py --info --extra --save > "output-$DATE-extra"  # this also generates dat.pkl
/bin/cp "dat.pkl" "dat-$DATE.pkl"