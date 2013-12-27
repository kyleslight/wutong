#!/bin/bash

if ! python -c "import tornado, requests";then exit 1;fi
psql -l | grep -wo wutong 1>/dev/null 2>&1 || createdb wutong
psql -l | grep -wo wutong_test 1>/dev/null 2>&1 && dropdb wutong_test
createdb wutong_test && echo "create database 'wutong_test'"
res=$(psql -fmodel/dbschema/schema.sql wutong_test 2>&1)
if [ ! $? -eq 0 ];then 
    echo "$res"
    exit 1
fi

echo "run unittest"
res=$(pytest test 2>&1)
if [ ! $? -eq 0 ];then
    echo "$res"
    exit 1
fi

#if [ "$1" = "test" ];then
if true;then
    echo 'gen random test data ...'
    res=$(python test/util.py 1 2>&1)
    if [ ! $? -eq 0 ];then
        echo "$res"
        exit 1
    fi
    echo 'finished!'
fi
