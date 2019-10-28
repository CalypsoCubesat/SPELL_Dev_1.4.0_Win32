#!/bin/bash

function die() {
    echo >&2 "$@"
    echo "Usage: $(basename $0) context path-to-procedure"
    exit 1
}

# capture signals
function signal_handler {
    pkill timeout
    i=$LIMIT
}
trap signal_handler HUP QUIT INT TERM

[ $# -eq 2 ] || die "Provide two args"
CONTEXT=$1
PROC=$2
[ -f $PROC ] || die "$PROC does not exist"

[ ! -z $SPELL_HOME ] || die "Please set the SPELL_HOME env variable"
[ ! -z $SPELL_CONFIG ] || die "Please set the SPELL_CONFIG env variable"
[ ! -z $SPELL_DATA ] || die "Please set the SPELL_DATA env variable"

EXC=fuzzproc.sh
[ -f `which $EXC` ] || die "Cannot find $EXC in PATH"

PROCNAME=`basename $PROC | rev | cut -f2- -d. | rev`
LOGDIR=spelldebugger-$CONTEXT-$PROCNAME-`date +%Y%m%d-%H-%M-%S`
mkdir $LOGDIR || die "Creating $LOGDIR failed"
cd $LOGDIR

LOG=log.txt

#############################
### MAIN LOOP STARTS HERE ###
#############################
RUNTIME=120
OLDCOV=0
COVCHECK=10
LIMIT=101
TIMEOUTCNT=0
TIMEOUTLIMIT=5
CRASHCNT=0
CRASHLIMIT=5
echo "Fuzzing $PROCNAME" >> $LOG
for ((i=1;i<=$LIMIT;i+=1)); do

    echo "== `date` ==" >> $LOG
    echo "i=$i" >> $LOG
    
    # check if we should replay or not
    CMD="$EXC $CONTEXT $RUNTIME $PROC"
    echo "CMD=$CMD" >> $LOG
    $CMD > /dev/null 2>&1
    
    CODE=$?
    # check return code
    case $CODE in
    0)
        # Reset timeout counter
        TIMEOUTCNT=0
        echo "TIMEOUTCNT=0" >> $LOG
        ;;
    124 | 137)
        # Timeout reached
        echo "## timeout -> $PROC" >> $LOG
        ((TIMEOUTCNT+=1))
        if [ $TIMEOUTCNT -eq $TIMEOUTLIMIT ]; then
            # penalize the procedure for subsequent timeouts
            ((LIMIT/=2))
            TIMEOUTCNT=0
            echo "$TIMEOUTLIMIT subsequent timeouts, penalizing to LIMIT=$LIMIT" >> $LOG
        fi
        echo "TIMEOUTCNT=$TIMEOUTCNT" >> $LOG
        ;;
    *)
        # Something went wrong
        echo "## crash -> $PROC" >> $LOG
        ((CRASHCNT+=1))
        if [ $CRASHCNT -eq $CRASHLIMIT ]; then
            # Too many unknown crashes, stop
            echo "$CRASHLIMIT crashes found, stoppping for investigation" >> $LOG
            i=$LIMIT
        fi
        echo "CRASHCNT=$CRASHCNT" >> $LOG
        ;;
    esac

    # TODO: retaing cov files once minimal test case set is implemented
    #COVDIR=cov
    #mkdir -p $COVDIR > /dev/null 2>&1
    #cp .coverage.* $COVDIR > /dev/null 2>&1

    # did the coverage increase? Check every now and then to spped up things
    if (( $i % $COVCHECK == 0 )); then
        coverage combine > /dev/null 2>&1
        COV=`coverage report $SPELL_DATA/Procedures/$CONTEXT/$PROCNAME.py  | tail -1 | tr -s ' ' | cut -d ' ' -f4 | cut -d'%' -f1`
        if [ $COV -gt $OLDCOV ]; then
            echo "Coverage increase: ${OLDCOV}%->${COV}%" >> $LOG
            OLDCOV=$COV
            # Reset the counter
            i=1
            echo "i=1" >> $LOG
        fi
        if [ $COV -eq 100 ]; then
            i=$LIMIT
            echo "Reached 100% coverage, stopping" >> $LOG
        fi
    fi

done
