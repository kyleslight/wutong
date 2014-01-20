#!/bin/sh

# run `memcached` if doesn't run
if ! ps aux | grep memcached | grep -v "grep memcached";then
    memcached &
fi
python main.py $@
