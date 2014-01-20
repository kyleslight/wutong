#!/bin/bash

# check python module
pycode="
modules = ['tornado', 'requests', 'Image']
sig = 0
for module in modules:
    try:
        __import__(module)
    except ImportError:
        print('Need python module: ' + module)
        sig = 1
exit(sig)
"
if ! python -c "$pycode"
then
    exit 1
fi

function is_cmd_exists {
    if [ ! which "$1" &> /dev/null ]
    then
        echo "Need command: $1"
        return 1
    fi
    return 0
}

if ! is_cmd_exists "psql"
then
    exit 1
fi
psql -l | grep -wo wutong 1>/dev/null 2>&1 || createdb wutong
psql -l | grep -wo wutong_test 1>/dev/null 2>&1 && dropdb wutong_test
createdb wutong_test && echo "create database 'wutong_test'"
res=$(psql -f model/dbschema/schema.sql wutong_test 2>&1)
if [ ! $? -eq 0 ]
then
    echo "$res"
    exit 1
fi

if is_cmd_exists "py.test"
then
    echo "run unittest"
    res=$(py.test test 2>&1)
    if [ ! $? -eq 0 ]
    then
        echo "$res"
        exit 1
    fi
fi

#if [ "$1" = "test" ];then
if true
then
    # num = $2 or 1
    num=${2-1}
    echo 'gen random test data ...'
    res=$(python test/util.py $num 2>&1)
    if [ ! $? -eq 0 ]
    then
        echo "$res"
        exit 1
    fi
    echo 'finished!'
fi
