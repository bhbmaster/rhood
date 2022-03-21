#!/bin/bash
#
# Last update: 2022-03-20
#
# filename: rhood/archive/parse-output.sh
# usage: .\parse-output.sh      # shows results on screen
# usage: .\parse-output.sh save # saves results to file to parse.out with start and end date and how long it took
#
# what this does: shows oneline info of profits from each run of rhood
# format of output:
# 2022-03-19 17:01:55  -  * STOCK total net profit $3318.65 * CRYPTO total net profit $1884.15 * total profit from stocks, crypto, and options + dividends: $5227.43
# 2022-03-19 18:01:56  -  * STOCK total net profit $3318.65 * CRYPTO total net profit $1884.15 * total profit from stocks, crypto, and options + dividends: $5227.43
#
###############################################

# for scheduler (doesn't hurt anything anyways)
PATH="/usr/bin:/usr/local/bin:$PATH"

# We must start from the archive dir
SCRIPT_DIR=$( cd -- "$( dirname -- "$0" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"  # we need to get to output dir in SCRIPT_DIR, so first make sure we are there
cd output;

SHOW_OLD=1 # 0 no 1 yes
SHOW_NEW=1 # 0 no 1 yes
OUTPUT_SAVEFILE="$SCRIPT_DIR/parse.out" # we save it to same dir as script

#-------------------------------- analyze old files --------------------------#
# these ones are txt compressed xz files created by rotate.sh, so we have to extract them in chronological order
# the filename (which has the date) is prefixed to everyline, which makes it useful
# during this extraction process.
# the files have the date in yyyy-mm-dd HH:MM order, so they are read in order from oldest to newest
# also within eachfile they are ordered from oldest to newest. thus order is always maintained from oldest to newest.
# NOTE: when these compressed files are analyzed their dates are written in format yyyy-mm-dd HH:MM:XX as that is all we keep in the filename
function show_old () {
	CONCAT="";
	OLD_INPUT_DATE=""
	xzcat $(ls -1tr output*txt.xz) 2> /dev/null | \
	# FOR TEST # xzcat output-from-2022-03-20-0200-to-2022-03-20-1700.txt.xz 2> /dev/null | \ 
	grep "total.*profit" | \
	grep -v "total net profit from stocks" | while read i; do
		# ((N++))
		INPUT_DATE=$(echo "$i" | cut -d: -f1 | cat -e);
		REMAINING=$(echo "$i" | cut -d: -f2- | cat -A | sed 's|\^M||g' | sed 's|$$||g');
		# echo "(R $REMAINING)"
		CONCAT="${CONCAT}${REMAINING}";
		OLD_INPUT_DATE=$INPUT_DATE;
		# we can print out the results if we encountered the last sentence we need to see
		if echo "$REMAINING" | grep -q "total profit from stocks"; then
			# echo "LAST ONE:"
			MOD_DATE=$(echo "$INPUT_DATE" | sed 's|output-||g;s|.txt\$||g;s|\.txt||g' | sed 's|\([0-9]*-[0-9]*-[0-9]*\)-\([0-9][0-9]\)\([0-9][0-9]\)|\1 \2:\3:XX|')
	        echo "${MOD_DATE}  - ${CONCAT}" # | sed 's|\^M\$||g';
	        CONCAT=""
		fi
	done;
}


#-------------------------------- analyze current files --------------------------#
# cat -A is needed as there are weird meta ^M characters that throw off the newline output
# we then use sed to clean up the ^M and $ (at end of string) occurances
# NOTE: when these uncompressed files are analyzed their dates are written in format yyyy-mm-dd HH:MM:## from stat output
function show_new () {
	ls -1tr output*txt 2> /dev/null | while read i; do
		set -f # so that * are not expanded. we don't want it at the top of script as then other stuff might not work and a while loop is in a way a subshell
		# MOD_DATE=$( stat -c "%w" $i | cut -f1 -d"."; )
		MOD_DATE=$(echo "$i" | sed 's|output-||g;s|.txt\$||g;s|\.txt||g' | sed 's|\([0-9]*-[0-9]*-[0-9]*\)-\([0-9][0-9]\)\([0-9][0-9]\)|\1 \2:\3:##|')
		echo  "$MOD_DATE - " $( cat $i | grep "total.*profit" | grep -v "total net profit from stocks"; );
	done | grep -v " - $" | cat -A | sed 's|\^M||g' | sed 's|$$||g'
}

#-------------------------------- rotate old files --------------------------#
# ./rotate.sh # <--- only do this if we run analyze like once a week or something (so that we have some good amount of files to rotate)

##### MAIN #####

if  [[ "$1" == "save" ]]; then
	STARTDATE_STRING=`date`; STARTDATE=`date +%s`
	echo "* Parsing output started at $STARTDATE_STRING $STARTDATE"
	echo "* Running and saving to $OUTPUT_SAVEFILE"
	echo "* Optionally, follow along in another window with: tail -f $OUTPUT_SAVEFILE"
	{
		echo "PARSE START @ $STARTDATE_STRING $STARTDATE"
		[[ "$SHOW_OLD" ==  1 ]] && show_old;
		[[ "$SHOW_NEW" ==  1 ]] && show_new;
		ENDDATE_STRING=`date`; ENDDATE=`date +%s` # these will be called outside of the process group {}
		DIFFDATE=`echo "$STARTDATE $ENDDATE" | awk '{print $2-$1}'` # these will be called outside of the process group {}
		echo "PARSE END @ $ENDDATE_STRING $ENDDATE (took $DIFFDATE seconds)"
	} > "$OUTPUT_SAVEFILE" 2>&1
	echo "* Parsing output finished at $ENDDATE_STRING $ENDDATE (took $DIFFDATE seconds)"
	echo "* Operation Complete"
else
	[[ "$SHOW_OLD" ==  1 ]] && show_old;
	[[ "$SHOW_NEW" ==  1 ]] && show_new;
fi

exit 0
# EOF
