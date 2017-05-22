#!/usr/bin/env bash


pwd=$(cd `dirname $0`;pwd)
DEAMON=-d
VER=$1

#database 
#please  edit postgresql.conf and  pg_hdb.conf  first !!
docker run --name rhino_db $DEAMON -it -v $pwd/../:/opt -p 15432:5432   rhino_0.2 /bin/bash


# setenforce 0 