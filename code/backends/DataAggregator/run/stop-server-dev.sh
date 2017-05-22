#!/bin/bash

export LC_ALL=en_US.UTF-8
pwd=$(cd `dirname $0`;pwd)

cat $pwd/server.pid | xargs kill -9
