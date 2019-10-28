#!/bin/bash

function die() {
  echo >&2 "$@"
  echo "Usage: $(basename $0) context"
  exit 1
}

[ ! -z $SPELL_HOME ] || die "Please set the SPELL_HOME env variable"
[ ! -z $SPELL_CONFIG ] || die "Please set the SPELL_CONFIG env variable"
[ ! -z $SPELL_DATA ] || die "Please set the SPELL_DATA env variable"

[ $# -eq 1 ] || die "Please provide one argument"
CONTEXT=$1

CONTEXTCONFIG=$SPELL_CONFIG/contexts/context_$CONTEXT.xml
[ -f $CONTEXTCONFIG ] || die "Context config $CONTEXTCONFIG not deplyed?"

SERVERCONFIG=$SPELL_CONFIG/server/server_$CONTEXT.xml
[ -f $SERVERCONFIG ] || die "Server config $SERVERCONFIG not deployed?"

INPUT=$SPELL_DATA/InputFiles/$CONTEXT
OUTPUT=$SPELL_DATA/OutputFiles/$CONTEXT
PROCS=$SPELL_DATA/Procedures/$CONTEXT
USERLIB=$SPELL_DATA/UserLib/$CONTEXT
[ -d $INPUT ] || die "$INPUT does not exist"
[ -d $OUTPUT ] || die "$OUTPUT does not exist"
[ -d $PROCS ] || die "$PROCS does not exist"
[ -d $USERLIB ] || die "$USERLIB does not exist"

rm -rf $INPUT || die "Deleting $INPUT failed"
rm -rf $OUTPUT || die "Deleting $OUTPUT failed"
rm -rf $PROCS || die "Deleting $PROCS failed"
rm -rf $USERLIB || die "Deleting $USERLIB failed"
rm -f $CONTEXTCONFIG
rm -f $SERVERCONFIG

echo "Done."
