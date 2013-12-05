#!/bin/sh

if ! python -c "import tornado, requests";then exit 1;fi
psql -l | grep -wo wutong 1> /dev/null 2>&1 || createdb wutong
psql -l | grep -wo wutong_test 1> /dev/null 2>&1 && dropdb wutong_test
createdb wutong_test
res=$(python test/models.py debug 2>&1)
if echo "$res" | grep -i "FAILED" > /dev/null;then
    echo "$res"
fi
