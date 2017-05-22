#!/bin/bash
export PATH=$PATH:/usr/pgsql-9.4/bin

pwd=$(cd `dirname $0`;pwd)

mkdir -p /opt/redis
redis-server /opt/scripts/redis.conf
#chown redis /opt/redis
#su - redis -c "redis-server"

