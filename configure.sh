#!/bin/bash

function is_cmd_exists {
    if [ ! which "$1" &> /dev/null ]
    then
        echo "Need command: $1"
        return 1
    fi
    return 0
}

function execute_sql {
    echo "executing $1"
    res=$(psql -q -v ON_ERROR_STOP=true -f model/dbschema/$1 wutong_test 2>&1)
    if [ ! $? -eq 0 ]
    then
        echo "$res"
        echo "ERROR: execute $1"
        exit 1
    fi
}

function unittest {
    echo "run unittest..."
    py.test test
    if [ ! $? -eq 0 ]
    then
        echo "ERROR: unittest"
        exit 1
    fi
}

function gentestdata {
    echo 'gen random test data ...'
    num=${1-1} # $1 or 1
    res=$(python test/util.py $num 2>&1)
    if [ ! $? -eq 0 ]
    then
        echo "$res"
        exit 1
    fi
    echo 'finished!'
}

function clean {
    psql -l | grep -wo wutong_test 1>/dev/null 2>&1 && dropdb wutong_test
    rm -vf ./static/uploads/* ./static/avatar/*.png ./*.pyc ./**/*.pyc
}

function run {
    if ! ps aux | grep memcached | grep -v "grep memcached";then
        memcached &
    fi
    python main.py $@
}

case "$1" in
    "run" )
        run ${@:2}
        ;;
    "clean" )
        clean
        ;;
    "unittest" )
        unittest
        ;;
    "gendata" )
        gentestdata ${2-1}
        ;;
    "updatedb" )
        if [ "$2" = "function" ]
        then
            execute_sql "function.sql"
        else
            execute_sql "schema.sql"
            execute_sql "function.sql"
        fi
        ;;
    * )
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

        if ! is_cmd_exists "psql"
        then
            exit 1
        fi
        psql -l | grep -wo wutong 1>/dev/null 2>&1 || createdb wutong
        psql -l | grep -wo wutong_test 1>/dev/null 2>&1 && dropdb wutong_test
        createdb wutong_test && echo "create database 'wutong_test'"
        execute_sql "schema.sql"
        execute_sql "function.sql"

        # if is_cmd_exists "py.test"
        # then
        #     unittest
        # fi
        # TODO: remove
        # gentestdata
        ;;
esac
