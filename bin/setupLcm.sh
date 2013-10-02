#!/bin/sh
# A script to be run before running a Python module to make sure we can 
# use our lcm types and send multicast messages

export PYTHONPATH="$PYTHONPATH:../src:../src/lcmtypes"
export LCM_DEFAULT_URL=udpm://239.255.76.67:7667?ttl=1

$@
