#coding:utf-8


import sqlite3
import os.path
import os

from camel.fundamental.utils.pinyin import spm,pinyin as PINYIN
from camel.fundamental.application.app import instance
from camel.fundamental.utils.useful import Singleton
from camel.rhinoceros.base import MovableObject,DataEnvelope,YES,NO



SQL_MO_TABLE="""
CREATE TABLE movable_object (
  id TEXT PRIMARY KEY NOT NULL,
  time  INTEGER,
  provider INTEGER,
  data TEXT,
  spm VARCHAR(20)

);
CREATE UNIQUE INDEX mo_buffers_id_uindex ON movable_object (id);
CREATE INDEX mo_buffers_spm_index ON movable_object (spm);
"""

# GlobalMovableObjectBuffer

class MovableObjectBuffer(Singleton):
    """数据缓冲池
    """
    def __init__(self,name):
        self.name = name
        self.mos = {}  # {plate: obj (VehicleObject) }
        # self.dbconn = None
        self.memconn = None
        self.cfgs = {}
        self.diffs = {}  # 差异变动的mo

    # def set(self,mo_id,data):
    #     """
    #     1.加入新的车辆标识到内存数据库用于之后的车牌名称检索
    #
    #     :param mo_id: 车辆唯一标识
    #     :type mo_id: basestring
    #     :param data:
    #     :type data: DataEnvelope or DataCategory
    #     """
    #     mo = self.mos.get(mo_id)
    #     if not mo:
    #         mo = MovableObject(mo_id)
    #         self.mos[mo_id] = mo
    #         self.memconn.execute("insert into movable_object values(?,0,0,'')",(mo_id,))
    #     if mo.update(data) == YES:
    #         self.diffs[mo.getId()] = mo #数据更新了
    #         return mo
    #     return None

    def set(self,new):
        """
        数据变动则返回变动的mo对象
        :param new:
        :return:
        """
        diff = None
        if not self.mos.has_key(new.getId()):
            self.mos[new.getId()] = new
            pinyin = PINYIN(new.getId())
            self.memconn.execute("insert into movable_object values(?,0,0,'',?)", (new.getId(),pinyin))
            self.memconn.commit()
            diff = new
        else:
            old = self.mos.get(new.getId())
            if old.update(new) == YES: # 位置变动了
                diff = old
        return diff


    def get(self,mo_id):
        return self.mos.get(mo_id)

    def remove(self,mo_id):
        self.memconn.execute("delete from movable_object where id=?", (mo_id,))

    def filterNames(self,moid,result,func=None):
        """
        车辆名称模糊匹配标识
        :param moid:
        :param limit:
        :return:
        """
        id = PINYIN(moid)
        cur = self.memconn.cursor()
        if id:
            cur.execute("select id from movable_object where spm like ? order by spm ",(id+'%',))
        else:
            cur.execute("select id from movable_object  order by spm ")


        for row in cur:
            id = row[0]
            if id.find(moid) == -1:
                continue
            if func:
                func(id,result)
            else:
                result.append(id)


    def init(self,cfgs,action=None):
        """初始化数据

        1.从本地缓存文件读取最近的车辆位置数据
        2.创建内存数据库用于基于sql的查询

        :param cfgs:
        :param action: 初始化mo之后执行的动作
        :return:
        """
        self.cfgs = cfgs

        self.memconn = sqlite3.connect(":memory:")
        self.memconn.executescript(SQL_MO_TABLE)

        # self.loadCachedData()

        for mo in self.mos.values():
            action(mo)


    def loadCachedData(self):
        """启动时从本地db中加载所有的定位信息"""
        path = os.path.join(instance.getDataPath(), self.cfgs.get('cache_file', 'location.db'))
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        for row in cur.execute('select * from mo_buffers'):
            moid,data,time = row[0],row[1],row[2]
            mo = MovableObject.unmarshall(data)
            if mo :
                self.mos[mo.id] = mo
        conn = None

    def saveCacheData(self):
        """写入所有车辆状态数据到本地数据库"""

        path = os.path.join(instance.getDataPath(), self.cfgs.get('cache_file', 'location.db'))
        os.remove(path)

        conn = sqlite3.connect(path)
        conn.executescript(SQL_MO_TABLE)

        for k,v in self.mos.items():
            conn.execute("insert into movable_object values(?,0,0,?)",(k,v.marshall()))
        conn = None

    def getDifferences(self,clear=True):
        """取得差异数据,定时服务进行推送或者查询返回"""
        diffs = self.diffs
        if clear:
            self.diffs = {}
        return diffs



"""
车辆->位置数据->用户->接入服务器->浏览器

"""

