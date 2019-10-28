#!/usr/bin/env python

import os, sys, random
import string

seed = os.getenv("SPELL_RANDOM_SEED")
if seed:
    random.seed(seed)

proc = []
with open(sys.argv[1]) as f:
    proc = f.readlines()
spb = []
with open(sys.argv[2]) as f:
    spb = f.readlines()

# Get Var definitions
res = []
for line in proc:
    if "=Var(" in line:
        key = line.split("'")[1]
        key += ":="
        found = False
        for line2 in spb:
            # key must be defined
            if key in line2 and key != line2.strip():
                found = True
                break
        if not found:
            res.append((key, line))

# Create valid values
# $DELTA_MOM_CONS ARGS['$DELTA_MOM_CONS']=Var(Type=FLOAT, Range=[ 0.0, 1.0 ], Default=1E-05, Confirm=False)
ret = []
for key, val in res:
    prefix = val.split("=Var")[0].strip()
    v = val.split("=Var")[1].strip("()\n\r")
    typ = None
    default = None
    rang = None
    expected = None
    if "Type" in v:
        typ = v.split("Type=")[1]
        if typ.endswith(")"):
            typ = typ.strip(")")
        else:
            typ = typ.split(",")[0]
    if "Default" in v:
        default = v.split("Default=")[1]
        if default.endswith(")"):
            default = default.strip(")")
        else:
            default = default.split(",")[0]
    if "Range" in v:
        rang = v.split("Range=")[1]
        if rang.endswith(")"):
            rang = rang.strip(")")
        else:
            rang = rang.split("]")[0] + "]"
    if "Expected" in v:
        expected = v.split("Expected=")[1]
        if expected.endswith(")"):
            expected = expected.strip(")")
        else:
            expected = expected.split("]")[0] + "]"
    assert typ
    #print "Type=" + repr(typ) + ", Default=" + repr(default) + ", Expected=" + repr(expected) + ", Range=" + repr(rang)
    ret.append((prefix, typ, default, rang, expected, val))

res = []
for r in ret:
    prefix, typ, default, rang, expected, val = r
    #print val,
    s = prefix + "="
    if default:
        s += default
    elif expected:
        s += random.choice(expected.strip("[]").strip().split(",")).strip()
    elif typ == "STRING":
        s += "'" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randint(1, 20))) + "'"
    elif typ == "FLOAT":
        if rang:
            a = float(rang.strip("[]").strip().split(",")[0].strip())
            b = float(rang.strip("[]").strip().split(",")[1].strip())
            s += str(random.uniform(a, b))
        else:
            s += str(random.uniform(-20, 20))
    elif typ == "LONG":
        if rang:
            a = rang.strip("[]").strip().split(",")[0].strip()
            if 'x' in a:
                a = int(a, 0)
            else:
                a = int(a)
            b = rang.strip("[]").strip().split(",")[1].strip()
            if 'x' in b:
                b = int(b, 0)
            else:
                b = int(b)
            s += str(random.randint(a, b))
        else:
            s += str(random.randint(-100, 100))
    elif typ == "ABSTIME":
        s += "'01-01-2015 13:33:00'"
    elif typ == "RELTIME":
        s += "'+00:00:20'"
    res.append(s)

prev = ""
for line in proc:
    if "Step('INIT', 'Confirm procedure execution')" in line:
        print "Merge_SPB(ARGS)"
        for v in res:
          print v
        print "#"
    elif "Finish('Execution aborted by user')" in line and "Do you really want to execute procedure" in prev:
        line = line.rstrip("\r\n") + " # pragma: no cover\r\n"
    print line,
    prev = line
