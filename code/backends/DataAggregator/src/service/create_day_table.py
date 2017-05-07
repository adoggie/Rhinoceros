#coding:utf-8

"""
create_day_table.py

创建多日天的数据库表

"""

import time
from camel.fundamental.utils.timeutils import timestamp_to_str
import psycopg2

SQL_TABLE="""
CREATE TABLE {table}
(
    id VARCHAR(20) NOT NULL,
    time INTEGER,
    data JSONB,
    last JSONB,
    PRIMARY KEY (id, time)
);
CREATE INDEX {table}_id_index ON {table} (id);
CREATE INDEX {table}_time_index ON {table} (time);
CREATE INDEX {table}_time_id_index ON {table} (id,time);
"""

host='ytodev2'
db='rhino'
port=5432
user='postgres'
password='13916624477'


conn = psycopg2.connect(host=host,port=port,user=user,password=password,dbname=db)
conn.autocommit = True
#conn.set_session(readonly=True, autocommit=True)

def create_day_table(days):
    seconds_day = 3600*24
    start = time.time()-seconds_day
    for _ in range(days):
        table = 'mo_data_'+timestamp_to_str(start, fmt='%Y%m%d')
        sql = SQL_TABLE.format(table=table)

        start+=seconds_day
        try:
            cur = conn.cursor()
            cur.execute(sql)
        except:
            pass
        print sql



if __name__=='__main__':
    create_day_table(100)