#!/bin/bash
export PATH=$PATH:/usr/pgsql-9.4/bin

pwd=$(cd `dirname $0`;pwd)

su - postgres -c "pg_ctl -D /opt/pgsql stop"

