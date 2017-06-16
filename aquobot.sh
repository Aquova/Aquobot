#!/bin/sh

while :
do
    if ! pgrep -x "aquobot.py" > /dev/null
    then
        python3 aquobot.py
    fi
done
