#!/bin/sh
# Sets up multicast when no network is connected. 

function displayHelp {
	echo "Usage:   enableLocalMulticastLinux.sh"
	exit 1
}

if [ "$1" = "--help" ]; then
	displayHelp
fi

if [ "$(id -u)" != 0 ]; then
	echo "This script must be run as root" 1>&2
	exit 1
fi

ifconfig lo multicast
route add -net 224.0.0.0 netmask 240.0.0.0 dev lo
