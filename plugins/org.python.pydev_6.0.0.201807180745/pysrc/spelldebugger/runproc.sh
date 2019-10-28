#!/bin/bash

# This script takes a procedure and runs it using a random seed.
# It must exist in SPELL_DATA/...

# helper
function die() {
    echo >&2 "$@"
    echo "Usage: $(basename $0) context seed runtime path-to-proc-in-spell-data [optional args]"
    exit 1
}

[ $# -ge 4 ] || die "Provide at least 4 args"
CONTEXT=$1
SEED=$2
RUNTIME=$3
PROC=$4

# checks
[ ! -z $SPELL_HOME ] || die "Please set the SPELL_HOME env variable"
[ ! -z $SPELL_CONFIG ] || die "Please set the SPELL_CONFIG env variable"
[ ! -z $SPELL_DATA ] || die "Please set the SPELL_DATA env variable"

EXC=$SPELL_HOME/bin/SPELL-ExecutorCmd
[ -f $EXC ] || die "$EXC does not exist"

DIR=$(dirname $PROC)
[ "$DIR" == "$SPELL_DATA/Procedures/$CONTEXT" ] || die "Proc is not in $SPELL_DATA/Procedures/$CONTEXT"

CONTEXTCONFIG=$SPELL_CONFIG/contexts/context_$CONTEXT.xml
[ -f $CONTEXTCONFIG ] || die "Context config $CONTEXTCONFIG not found"
SERVERCONFIG=$SPELL_CONFIG/server/server_$CONTEXT.xml
[ -f $SERVERCONFIG ] || die "Server config $SERVERCONFIG not found"

# run
export SPELL_CONTEXT=$CONTEXT
export SPELL_RANDOM_SEED=$SEED
KILLTIME=$(($RUNTIME*2))
PROCNAME=`basename $PROC | rev | cut -d. -f2- | rev`
shift 4
timeout -k $KILLTIME $RUNTIME $EXC -p $PROCNAME#0 -c $SERVERCONFIG -n $CONTEXT $@

# return code of timeout
exit $?
