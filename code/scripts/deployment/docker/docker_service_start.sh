#!/usr/bin/env bash


pwd=$(cd `dirname $0`;pwd)
DEAMON=-d
VER=$1

# services
docker run --name rhino_service $DEAMON -it -v $pwd/../:/opt    -p 15001:15001 -p 15002:15002 -p 15003:15003  rhino_0.2 /bin/bash
