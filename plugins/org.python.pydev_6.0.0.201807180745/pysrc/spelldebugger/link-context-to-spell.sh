#!/bin/bash

function die() {
  echo >&2 "$@"
  echo "Usage: $(basename $0) context path-to-sat-dir"
  exit 1
}

[ ! -z $SPELL_HOME ] || die "Please set the SPELL_HOME env variable"
[ ! -z $SPELL_CONFIG ] || die "Please set the SPELL_CONFIG env variable"
[ ! -z $SPELL_DATA ] || die "Please set the SPELL_DATA env variable"

[ $# -eq 2 ] || die "Please provide two arguments"
CONTEXT=$1
SATDIR=$2

[ -d $SATDIR ] || die "$SATDIR dir does not exist"

CF=context_$CONTEXT.xml
[ ! -f $SPELL_CONFIG/contexts/$CF ] || die "Context config for $CONTEXT already deployed?!"
CONTEXTCONFIG="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/contexts/$CF
[ -f $CONTEXTCONFIG ] || die "Context config $CONTEXTCONFIG is not available"

SF=server_$CONTEXT.xml
[ ! -f $SPELL_CONFIG/server/$SF ] || die "Server config for $CONTEXT already deployed?!"
SERVERCONFIG="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/contexts/$SF
[ -f $SERVERCONFIG ] || die "Server config $SERVERCONFIG is not available"

SATINPUT=$SATDIR/InputFiles
SATOUTPUT=$SATDIR/OutputFiles
SATPROCS=$SATDIR/Procedures
SATUSERLIB=$SATDIR/UserLib
[ -d $SATINPUT ] || die "$SATINPUT dir does not exist"
[ -d $SATPROCS ] || die "$SATPROCS dir does not exist"
[ -d $SATUSERLIB ] || die "$SATUSERLIB dir does not exist"

INPUT=$SPELL_DATA/InputFiles/$CONTEXT
OUTPUT=$SPELL_DATA/OutputFiles/$CONTEXT
PROCS=$SPELL_DATA/Procedures/$CONTEXT
USERLIB=$SPELL_DATA/UserLib/$CONTEXT
[ ! -d $INPUT ] || die "$INPUT already exists"
[ ! -d $OUTPUT ] || die "$OUTPUT already exists"
[ ! -d $PROCS ] || die "$PROCS already exists"
[ ! -d $USERLIB ] || die "$USERLIB already exists"

mkdir $INPUT || die "Creating $INPUT failed"
mkdir $OUTPUT || die "Creating $OUTPUT failed"
mkdir $PROCS || die "Creating $PROCS failed"
mkdir $USERLIB || die "Creating $USERLIB failed"

ln -s $SATINPUT/* $INPUT/
ln -s $SATUSERLIB/* $USERLIB/
cp $CONTEXTCONFIG $SPELL_CONFIG/contexts
cp $SERVERCONFIG $SPELL_CONFIG/server

echo "Done."
