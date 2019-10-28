#!/bin/bash

cnt=1
for i in `ls -d spell*`; do
    cd $i
    coverage combine
    cp .coverage ../.coverage.$cnt
    ((cnt+=1))
    cd ..
done

coverage combine
coverage report > coverage.txt
coverage html

grep home coverage.txt | sort -nr -k4 > coverage-sorted.txt

find . -name error*.log -exec tail -20 {} \; > error.txt
find . -name investigate*.log -exec tail -20 {} \; > investigate.txt
