#!/bin/bash
CORESEEK_DIR=/usr/local/coreseek
PID=`ps aux | grep searchd | grep -v "grep" | perl -pe 's/[ \t]+/ /g' | cut -d' ' -f2`
if [ ! -z "$PID" ]; then
    echo $PID
    $CORESEEK_DIR/bin/searchd -c ./etc/wutong.conf --stop &> /dev/null
fi
$CORESEEK_DIR/bin/indexer -c ./etc/wutong.conf --all
$CORESEEK_DIR/bin/searchd -c ./etc/wutong.conf 
