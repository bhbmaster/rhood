#!/bin/bash 

# test rhood's every argument, to make sure no errors.
# use either command below, then review the output file
# # nohup ./TestSuite.sh > test-output.txt 2>&1 &
# # ./TestSuite.sh > test-output.txt 2>&1 &

N=0

function LogNumberTrackerWrapper () {
    N=$((N+1));
    echo ""
    echo "###########################################";
    echo "### `date` | `date +%s` --- TEST $N: $@ ###";
    echo "###########################################";
    echo "";
    eval $@;
}

function LogDoneMessage () {
    echo "";
    echo "###########################################";
    echo "### `date` | `date +%s` --- TESTS DONE ###";
    echo "###########################################";
    echo "";
}

LogNumberTrackerWrapper python rhood.py --all-info
LogNumberTrackerWrapper python rhood.py --all-info --extra
LogNumberTrackerWrapper python rhood.py --all-info --save
LogNumberTrackerWrapper python rhood.py --all-info --save --csv
LogNumberTrackerWrapper python rhood.py --all-info --save --csv --extra
LogNumberTrackerWrapper python rhood.py --all-info --save --csv --profile-csv
LogNumberTrackerWrapper python rhood.py --all-info --load
LogNumberTrackerWrapper python rhood.py --all-info --load --csv
LogNumberTrackerWrapper python rhood.py --all-info --load --extra
LogNumberTrackerWrapper python rhood.py --all-info --load --csv --extra
LogNumberTrackerWrapper python rhood.py --all-info --load --csv --profile-csv

LogNumberTrackerWrapper python rhood.py --profile-info
LogNumberTrackerWrapper python rhood.py --profile-info --profile-csv

LogNumberTrackerWrapper python rhood.py --finance-info
LogNumberTrackerWrapper python rhood.py --finance-info --extra
LogNumberTrackerWrapper python rhood.py --finance-info --save
LogNumberTrackerWrapper python rhood.py --finance-info --save --csv
LogNumberTrackerWrapper python rhood.py --finance-info --save --csv --extra
LogNumberTrackerWrapper python rhood.py --finance-info --load
LogNumberTrackerWrapper python rhood.py --finance-info --load --csv
LogNumberTrackerWrapper python rhood.py --finance-info --load --extra
LogNumberTrackerWrapper python rhood.py --finance-info --load --csv --extra

LogNumberTrackerWrapper python rhood.py --all-info --sort-by-name

# Not testing all features, such as CLI login or insecure login. I don't have an insecure account, mine is secure (2 factor enabled). Also I don't want to test CLI securely, because then this output log file will have my credentials in them. So I will manually test the login types.

LogDoneMessage;