#!/bin/bash

pwd=$(cd `dirname $0`;pwd)

mkdir /opt/qpid
chown qpidd /opt/qpid
qpidd --data-dir /opt/qpid --auth no -d


