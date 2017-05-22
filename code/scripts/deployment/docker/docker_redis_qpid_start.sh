#!/usr/bin/env bash


pwd=$(cd `dirname $0`;pwd)
DEAMON=-d
VER=$1

#redis & qpid 
docker run --name rhino_redis_qpid $DEAMON -it -v $pwd/../:/opt -p 16379:6379 -p 15672:5672    rhino_0.2 /bin/bash
