#!/bin/bash
export PATH=$PATH:/usr/pgsql-9.4/bin

pwd=$(cd `dirname $0`;pwd)

echo 'waiting for database is ok..'
sleep 1
echo 'create database rhino..'
mkdir -p /opt/pgsql
chown postgres /opt/pgsql
su - postgres -c "pg_ctl initdb  -D /opt/pgsql"
su - postgres -c "rm -rf /opt/pgsql/postgresql.conf"
su - postgres -c "rm -rf /opt/pgsql/pg_hba.conf"
su - postgres -c "cp /opt/scripts/postgresql.conf  /opt/pgsql"
su - postgres -c "cp /opt/scripts/pg_hba.conf  /opt/pgsql"
sleep 1 
su - postgres -c "pg_ctl -D /opt/pgsql -l logfile start"
sleep 2
echo 'preparing db rhino..'
su - postgres -c "createdb rhino"
echo 'alter user role..'
su - postgres -c "psql -c \"alter user postgres with password '13916624477'\" "

