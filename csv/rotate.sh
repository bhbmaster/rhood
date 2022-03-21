#!/bin/bash
#
# Last update: 2022-03-21
#
# filename: rotate.sh
# what this does: rotates csv dirs into csv*tar.xz
#
#############################################################

# for scheduler (doesn't hurt anything anyways)
PATH="/usr/bin:/usr/local/bin:$PATH"

# variables for output
DATESUF=`date +%Y%m%d-%H%M%S`
LOG_CSV="rotate-$DATESUF.log"

# get to script dir rhood/csv
SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"  # we need to get to output dir in SCRIPT_DIR, so first make sure we are there

### compress and rotate csv dirs - run from csv dir and it creates a csv-from-DATE-to-DATE.tar.xz file in same dir 
( LSOUT=$(ls -1tr | grep -E "^[0-9]{8}-[0-9]{4}-")  # gets the items that start with
LENGTH=$(echo "$LSOUT" | grep -c .)
FIRSTDATE=$(echo "$LSOUT" | grep . | head -1 | cut -f1,2 -d"-")
LASTDATE=$(echo "$LSOUT" | grep . | tail -1 | cut -f1,2 -d"-")
FINALFILE="csv-from-$FIRSTDATE-to-$LASTDATE.tar.xz"
echo "** `date` starting csv dir rotate:"
echo "** found $LENGTH dirs to rotate/compress"
[[ "$LENGTH" -le 2 ]] && { echo "** need 3 or more dirs to rotate. exiting."; exit 3; }
echo "** `date` creating $FINALFILE from $LENGTH csv dirs:"
tar -Jcvvvf ${FINALFILE} ${LSOUT} | awk '{n+=1;print $0 "\t" n;}'
echo "** `date` final xzed file:"
ls -lhtr ${FINALFILE}
echo "** `date` done"
# # delete logic
echo "** `date` deleting original dirs:"
N=0
echo "$LSOUT" | grep . | while read i; do
	((N++))
	echo "Deleting $N/$LENGTH - $i";
	rm -vrf "$i";
done
echo "** `date` done"
) &> "$LOG_CSV" &

echo "* Creating $LOG_CSV can follow: tail -F $LOG_CSV"

exit 0
# EOF
