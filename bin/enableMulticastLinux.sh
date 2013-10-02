#!/bin/sh
# Sets up multicast on the desired network device

function displayHelp {
	echo "Usage:   enableMulticastLinux.sh [NETWORK_DEVICE]"
	echo "Example: enableMulticastLinux.sh eth0"
	exit 1
}

if [ -z "$1" -o "$1" = "--help" ]; then
	displayHelp
fi

if [ "$(id -u)" != 0 ]; then
	echo "This script must be run as root" 1>&2
	exit 1
fi

route add -net 224.0.0.0/4 dev $1
sysctl -w net.ipv4.ip_forward=1
