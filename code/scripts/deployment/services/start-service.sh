#!/bin/bash

export LC_ALL=en_US.UTF-8
pwd=$(cd `dirname $0`;pwd)

export CAMEL_LIB=/opt/libs
svc_path=$1/run/start-server-dev.sh

echo $svc_path
if [ -z $2 ]; then
	nohup bash $svc_path > /dev/null 2>&1 &
else
	if [ $2 = 'front' ]; then
	  bash $svc_path
	fi
fi