#coding:utf-8

import json
import traceback
import psycopg2,psycogreen
import gevent_psycopg2
gevent_psycopg2.monkey_patch()

from psycopg2.extras import Json

from camel.fundamental.application.app import instance
from camel.fundamental.utils.useful import Singleton
from camel.fundamental.utils.importutils import import_class
from camel.fundamental.utils.timeutils import timestamp_to_str

"""
每台车辆
"""

SQL_TABLE="""
CREATE TABLE mo_data_{ymd}
(
    id VARCHAR(20) NOT NULL,
    time INTEGER,
    data JSONB,
    last JSONB
);
CREATE INDEX mo_data_{ymd}_id_index ON mo_data_{ymd} (id);
CREATE INDEX mo_data_{ymd}_time_index ON mo_data_{ymd} (time);
"""

class PersistenceHandler(object):
    def __init__(self):
        pass

class PostgresHandler(PersistenceHandler):
    """
        https://pypi.python.org/pypi/psycopg2
        http://pythonhosted.org/psycopg2/
        http://initd.org/psycopg/

        postgresql 9.4+
        psycopg2 2.7+
        jsonb supported: 2.5.4+
                http://initd.org/psycopg/docs/extras.html


        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    """
    def __init__(self,cfgs):
        PersistenceHandler.__init__(self)
        self.cfgs = cfgs
        self.name = self.cfgs.get('name','')
        self.conn = None

    def open(self):
        self.conn = psycopg2.connect(host=self.cfgs.get('host'),
            port=self.cfgs.get('port'),
            dbname = self.cfgs.get('dbname'),
            user = self.cfgs.get('user'),
            password = self.cfgs.get('password')
            )
        self.conn.autocommit = True

    def write(self,start,span,datas):
        """写入车辆监控数据到pgsql
        :param datas
        :type datas:list  (mos)
        """
        if len(datas) == 0:
            return
        moid = datas[0].getId()
        cur = self.conn.cursor()
        table = "mo_data_"+ timestamp_to_str(start, fmt='%Y%m%d')
        sql = "insert into {table} values(%s,%s,%s,%s)".format(table=table)
        list =[]
        print 'mo location:',moid,' size:',len(datas)
        for ao in datas:
            list.append(ao.dict())
        lastest = list[-1] # todo. 还需要检查轨迹点是否有效
        try:
            cur.execute(sql,[moid,start,Json(list),Json(lastest)])
        except:
            traceback.print_exc()
            instance.getLogger().warning(traceback.format_exc())


class PersistenceManager(Singleton):
    def __init__(self):
        self.cfgs = None
        self.handlers = {}

    def init(self,cfgs):
        self.cfgs = cfgs
        for cfg in self.cfgs.get('handlers',[]):
            cls = import_class(cfg.get('entry'))
            handler =cls(cfg)
            self.handlers[handler.name] = handler
            handler.open()

    def getHandler(self,name):
        return self.handlers.get(name)

    def write(self,start,span,mos):
        """
        将mos写入持久层

        :param start: 数据开始时间
        :param span:  数据有效时间范围
        :param mos: 监控对象数据
        :return:
        """
        # datas=[]
        # for mo in mos:
        #     datas.append(mo)
        for _,handler in self.handlers.items():
            handler.write(start,span,mos)


