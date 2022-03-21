#!/bin/bash
#
# Last update: 2022-03-19
#
# filename: rotate.sh
# what this does: rotates and compresses output files from archive/output into a single .txt files which is then compressed with xz to become .txt.xz. this also rotates out by compressing all of the dat files into a tar file and then compressing it with xz.
#
#############################################################

# for scheduler (doesn't hurt anything anyways)
PATH="/usr/bin:/usr/local/bin:$PATH"

# variables for output
DATESUF=`date +%Y%m%d-%H%M%S`
LOG_OUTPUT="output/rotate-$DATESUF.log"
LOG_DAT="dat/rotate-$DATESUF.log"

# We must start from the archive dir
SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"  # we need to get to output dir in SCRIPT_DIR, so first make sure we are there

### compress and rotate output files - run from archive dir and it creates an output-from-DATE-to-DATE.txt.zx file in archive/output from all of the output*txt files in output
( FILENAMEPREFIX="output";
cd output
LSOUT=$(ls -1tr | grep "^${FILENAMEPREFIX}.*txt$")
LENGTH=$(echo "$LSOUT" | grep -c .)
FIRSTDATE=$(echo "$LSOUT" | grep . | head -1 | sed 's|output-||g;s|\.txt||g')
LASTDATE=$(echo "$LSOUT" | grep . | tail -1 | sed 's|output-||g;s|\.txt||g')
FINALFILE="output-from-$FIRSTDATE-to-$LASTDATE.txt"
N=0
echo "** `date` starting output files rotate:"
echo "** found $LENGTH files to rotate/compress"
[[ "$LENGTH" -le 2 ]] && { echo "** need 3 or more files to rotate. exiting."; exit 3; }
for i in $(echo "$LSOUT" | grep . | grep -v "$FINALFILE"); do
	((N++))
	echo "processed $N/$LENGTH $i into $FINALFILE" >&2  # progress of appending file content w/ date prefix to single file (this is not appended) as its stderr
	cat $i | awk -v PREFIX=$i '{print PREFIX": "$0}' # this is appended into the file as its stdout
done > ${FINALFILE} # since we are only redirecting stdout we get the benefit of having a progress output
echo "** `date` concatted $FINALFILE:"
ls -lhtr ${FINALFILE}
echo "** `date` xzing the file:"
xz -9 ${FINALFILE}
echo "** `date` final xzed file:"
ls -lhtr ${FINALFILE}*
# delete logic
echo "** `date` deleting original files:"
echo "$LSOUT" | grep . | while read i; do rm -vf "$i"; done
# echo "** `date` moving up one dir to archive/:"
# mv -v ${FINALFILE}* ..
echo "** `date` done"
) &> "$LOG_OUTPUT" &
# ) |& tee "notes-testing-xz-on-outputs-`date +%Y%m%d-%H%M%S`.out"

### compress and rotate dat files - run from archive dir and it creates a dat-from-DATE-to-DATE.tar.xz file in archive/dat from all of the dat*pkl files in output
( FILENAMEPREFIX="dat";
cd dat
LSOUT=$(ls -1tr | grep "^${FILENAMEPREFIX}.*pkl$")
LENGTH=$(echo "$LSOUT" | grep -c .)
FIRSTDATE=$(echo "$LSOUT" | grep . | head -1 | sed 's|dat-||g;s|\.pkl||g')
LASTDATE=$(echo "$LSOUT" | grep . | tail -1 | sed 's|dat-||g;s|\.pkl||g')
FINALFILE="dat-from-$FIRSTDATE-to-$LASTDATE.pkl.tar.xz"
echo "** `date` starting dat files rotate:"
echo "** found $LENGTH files to rotate/compress"
[[ "$LENGTH" -le 2 ]] && { echo "** need 3 or more files to rotate. exiting."; exit 3; }
echo "** `date` creating $FINALFILE from $LENGTH dat.*pkl files:"
tar -Jcvvvf ${FINALFILE} ${FILENAMEPREFIX}*pkl | awk -v LENGTH=$LENGTH '{n+=1;print $0 "\t" n"/"LENGTH;}'
echo "** `date` final xzed file:"
ls -lhtr ${FINALFILE}
echo "** `date` done"
# # delete logic
echo "** `date` deleting original files:"
echo "$LSOUT" | grep . | while read i; do rm -vf "$i"; done
# echo "** `date` moving up one dir to archive/:"
# mv -v ${FINALFILE} ..
echo "** `date` done"
) &> "$LOG_DAT" &
# ) |& tee "notes-testing-xz-on-dat-`date +%Y%m%d-%H%M%S`.out"

echo "* Creating $LOG_OUTPUT can follow: tail -F $LOG_OUTPUT"
echo "* Creating $LOG_DAT can follow: tail -F $LOG_DAT"

exit 0
# EOF
