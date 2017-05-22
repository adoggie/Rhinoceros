#coding:utf-8

# from psycopg2 import pool
# import psycopg2,psycogreen

import gevent_psycopg2
gevent_psycopg2.monkey_patch()
from psycopg2 import pool as psycopg2_pool
import psycopg2
from camel.fundamental.utils.importutils import import_function
from camel.fundamental.utils.useful import Singleton
from camel.rhinoceros.base import DataEnvelope,DataCategory
from map import  MapCell,GlobalMap
from buffer import  MovableObjectBuffer
from base import  VehicleStatus

class TraceService(Singleton):
    """定位主服务类"""
    def __init__(self):
        self.cfgs = {}
        self.map_grids ={}
        self.scale_levels ={}
        self.db_pool = None
        self.visible_scales = {}  #

    def init(self,cfgs):
        self.cfgs = cfgs
        self.initMapGrids()
        MovableObjectBuffer.instance('mo_buffer').init(self.cfgs,self.updateMovableObjectIntoMapCell)
        self.initDatabase()

        #  设置不同运行状态下的地图显示级别控制
        s1,s2 = map(int,self.cfgs.get('visible_scales',{}).get('running','').split('-'))
        self.visible_scales[VehicleStatus.RUNNING] = (s1,s2)
        s1, s2 = map(int, self.cfgs.get('visible_scales', {}).get('stopped', '').split('-'))
        self.visible_scales[VehicleStatus.STOPPED] = (s1, s2)
        s1, s2 = map(int, self.cfgs.get('visible_scales', {}).get('offline', '').split('-'))
        self.visible_scales[VehicleStatus.OFFLINE] = (s1, s2)

        return self

    def initDatabase(self):
        dbcfgs = self.cfgs.get('database',{})
        min = dbcfgs.get('pool',{}).get('min',5)
        max = dbcfgs.get('pool',{}).get('max',10) # 默认db pool size ( 5-10 )
        host = dbcfgs.get('host')
        port = dbcfgs.get('port')
        user = dbcfgs.get('user')
        password = dbcfgs.get('password')
        dbname = dbcfgs.get('dbname')
        if max >0:
            self.db_pool = psycopg2_pool.SimpleConnectionPool(min, max,
                    host=host, port = port,user=user, password=password,
                dbname=dbname)

    def getBuffer(self):
        return MovableObjectBuffer.instance()

    def getMapGridByScaleLevel(self,scalelevel):
        if scalelevel not in range(1,20): # baidu: 19 - 1
            return None
        scalelevel = abs(scalelevel-19)+1
        return self.scale_levels.get(scalelevel)

    def getMapGridByMaxScaleLevel(self):
        scales = sorted(self.scale_levels.keys())
        return self.scale_levels.get(scales[-1])


    def getMapGridByMinScaleLevel(self):
        scales = sorted(self.scale_levels.keys())
        return self.scale_levels.get(scales[0])     # 单元块最小的网格

    def isVehicleVisible(self,scale,status):
        """判别车辆状态在指定的缩放级别下是否可见"""
        scale = self.visible_scales.get(status)
        if not scale:
            return False
        s,e = scale[0],scale[1]
        if scale >=s and scale <=e:
            return True
        return False

    def initMapGrids(self):
        region = map(float,self.cfgs.get('china_region').strip().split(','))
        encode = self.cfgs.get('coordinate_encode','').strip()
        if encode:
            func = import_function(encode)
            region[0],region[1] = func(region[0],region[1])

        cfgs = self.cfgs.get('map_grids',[])
        for cfg in cfgs:
            name = cfg.get('name')
            size = map(float,cfg.get('cell_size').strip().split('x'))
            l1,l2 = map(int,cfg.get('scale_level').strip().split(','))
            mapgrid = GlobalMap(name,size,region)
            self.map_grids[name] = mapgrid
            for level in range(l1,l2+1):
                self.scale_levels[level] = mapgrid

    def updateMovableObjectIntoMapCell(self,mo):
        """将当前车辆位置关联到地图网格"""
        loc = mo.getData(DataCategory.LOC.value)
        if not loc:
            return
        # 处理所有地图网格规格
        # 跨网格时需要将mo在两个cell之间切换
        for grid in self.map_grids.values():
            cell = grid.getCell(loc.lon,loc.lat)
            if cell:
                cell.putObject(mo)


    def onDataRecieved(self,data):

        env = DataEnvelope.unmarshall(data)
        if env:
            mo = env.toMovableObject()

            # mo = None
            # for payload in env.getPayloads():
            #     mo = self.getBuffer().set(env.getId(),payload)
            #     # or
            #     # MovableObjectBuffer.instance().set(env.getId(),env)
            # if mo: # 如果有数据变动，更新到地图

            mo = self.getBuffer().set(mo) #
            if mo: # 数据变动了，更新到地图关联
                self.updateMovableObjectIntoMapCell(mo)


    def getDatabaseConnection(self):
        if self.db_pool:
            return self.db_pool.getconn()

        dbcfgs = self.cfgs.get('database', {})
        host = dbcfgs.get('host')
        port = dbcfgs.get('port')
        user = dbcfgs.get('user')
        password = dbcfgs.get('password')
        dbname = dbcfgs.get('dbname')
        conn = psycopg2.connect(host = host, port = port, user = user, password = password,dbname = dbname)
        return conn

    def freeDatabaseConnection(self,conn):
        if not conn:
            return self

        if self.db_pool:
            self.db_pool.putconn(conn)
            return self

        conn = None

        #http://initd.org/psycopg/docs/pool.html