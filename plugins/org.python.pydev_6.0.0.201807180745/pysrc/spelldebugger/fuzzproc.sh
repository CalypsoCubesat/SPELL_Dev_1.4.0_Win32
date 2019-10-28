#!/bin/bash

# This script takes a procedure, preprocess it, copies it to SPELL_DATA/...
# and runs it using a random seed

function die() {
    echo >&2 "$@"
    echo "Usage: $(basename $0) context runtime path-to-procedure [optional args]"
    exit 1
}

[ ! -z $SPELL_HOME ] || die "Please set the SPELL_HOME env variable"
[ ! -z $SPELL_CONFIG ] || die "Please set the SPELL_CONFIG env variable"
[ ! -z $SPELL_DATA ] || die "Please set the SPELL_DATA env variable"

[ $# -ge 3 ] || die "Please provide at three args"
CONTEXT=$1
RUNTIME=$2
PROC=$3
[ -f $PROC ] || die "$PROC does not exist"

DIR=$SPELL_DATA/Procedures/$CONTEXT
[ -d $DIR ] || die "$CONTEXT not deployed?!"

EXC=runproc.sh
[ -f `which $EXC` ] || die "Cannot find $EXC in PATH"
INIT=initvars.py
[ -f `which $INIT` ] || die "Cannot find $INIT in PATH"

# HACK: check for the SCDB
SCDB=`find -L $SPELL_DATA/InputFiles/$CONTEXT -name SCDB.DB`
[ -f $SCDB ] || die "SpacecraftDB SCDB.DB for context $CONTEXT not found"
SPB=`grep "SPB_Import_Files" $SCDB | cut -d "'" -f4`
SPB=$(basename $SPB)
SPB=`find -L $SPELL_DATA/InputFiles/$CONTEXT -name $SPB`
[ -f $SPB ] || die "SPB $SPB for context $CONTEXT not found"

# init random seed
SEED=`od -A n -t d -N 3 /dev/urandom | tr -d '-' | tr -d ' '`

# prepare test proc file
PROCNAME=`basename $PROC | rev | cut -f2- -d. | rev`
PROCFILENAME=$PROCNAME-$SEED.py
#TARGETPROC=$SPELL_DATA/Procedures/$CONTEXT/$PROCFILENAME
TARGETPROC=$PROCNAME.py
echo "from spellwrapper import *" > $TARGETPROC
$INIT $PROC $SPB >> $TARGETPROC
exit

# tell the executor to track coverage
export SPELL_COV_LOG=`pwd`/.coverage.$SEED
export SPELL_COV_TRACK_LINES=1

LOG=proc-$SEED.log

# run
shift 3
$EXC $CONTEXT $SEED $RUNTIME $TARGETPROC $@ 2>&1 | tee $LOG

# check the return code
CODE=${PIPESTATUS[0]}
REASON=""
case $CODE in
0)
    # TODO: Check for different SPELL errors
    grep -q "Execution aborted" $LOG
    if [[ "$?" == "0" ]]; then
        REASON="error"
        CODE=666
    fi
    ;;
124 | 137)
    # Timeout reached
    ;;
*)
    # Something went wrong
    REASON="investigate"
    ;;
esac

# store logs in case of error
if [ ! -z $REASON ]; then
    cp $TARGETPROC $REASON-$PROCFILENAME > /dev/null 2>&1
    cp $LOG $REASON-$PROCFILENAME.log > /dev/null 2>&1
fi

# rename and move the test file
mv $TARGETPROC $SPELL_DATA/Procedures/$CONTEXT/$PROCNAME.py > /dev/null 2>&1

# fix path name for coverage tracking
if [ -f $SPELL_COV_LOG ]; then
    if [ -s $SPELL_COV_LOG ]; then
        sed -i s/"$PROCFILENAME"/"$PROCNAME".py/g $SPELL_COV_LOG > /dev/null 2>&1
    fi
else
    rm -f $SPELL_COV_LOG > /dev/null 2>&1
fi

# delete the log
rm -f $LOG > /dev/null 2>&1

# return timeout code
exit $CODE
