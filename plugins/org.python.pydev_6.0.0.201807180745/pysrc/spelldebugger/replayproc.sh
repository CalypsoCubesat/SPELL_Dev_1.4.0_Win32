#!/bin/bash

# This takes a proc executed before that contains the random seed in the file name,
# copies it to SPELL_DATA/... and executes it again using runproc.sh.
# It should return the same execution result, otherwise we have a bug

function die() {
    echo >&2 "$@"
    echo "Usage: $(basename $0) context runtime path-to-proc-to-replay [optional args]"
    exit 1
}

[ $# -ge 3 ] || die "Provide at least three args"
CONTEXT=$1
RUNTIME=$2
PROC=$3
[ -f $PROC ] || die "$PROC does not exist"

# Extract the seed from the proc file name
SEED=`basename $PROC | rev | cut -d. -f2- |  cut -d- -f 1 | rev`
RE='^[0-9]+$'
[[ $SEED =~ $RE ]] || die "Cannot find random seed in $PROC"

EXC=runproc.sh
[ -f `which $EXC` ] || die "Cannot find $EXC in PATH"

# copy the proc to the right place in $SPELL_DATA
[ ! -z $SPELL_DATA ] || die "Please set the SPELL_DATA env variable"
DIR=$SPELL_DATA/Procedures/$CONTEXT
[ -d $DIR ] || "$CONTEXT not deployed?!"
TARGETPROC=$DIR/$(basename $PROC)
cp $PROC $TARGETPROC

shift 3
$EXC $CONTEXT $SEED $RUNTIME $TARGETPROC $@
