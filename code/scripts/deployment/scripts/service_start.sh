#!/bin/bash

export LC_ALL=en_US.UTF-8
pwd=$(cd `dirname $0`;pwd)


nohup bash $pwd/scripts/gws.sh > /dev/null 2>&1 &
nohup bash $pwd/scripts/mexs.sh > /dev/null 2>&1 &

nohup bash $pwd/scripts/server.sh  > /dev/null 2>&1 &
nohup bash $pwd/scripts/soffice.sh  > /dev/null 2>&1 &
nohup bash $pwd/scripts/uwsgi.sh  > /dev/null 2>&1 &
