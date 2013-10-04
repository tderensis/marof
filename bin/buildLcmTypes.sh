#!/bin/sh

cd ../src/lcm-defs

lcm-gen -pj *.lcm
javac -cp /usr/local/share/java/lcm.jar marof_lcm/*.java
jar cf marof_lcm.jar marof_lcm/*.class
