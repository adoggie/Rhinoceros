#!/bin/bash
export PATH=$PATH:/usr/pgsql-9.4/bin

pwd=$(cd `dirname $0`;pwd)

redis-shutdown 
#chown redis /opt/redis
#su - redis -c "redis-server"

