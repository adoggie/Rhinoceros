#coding:utf-8

"""
https://github.com/zacharyvoase/gevent-psycopg2
http://initd.org/psycopg/docs/

"""

import json
import datetime
from camel.rhinoceros.base import TypeBase,MovableObject
from camel.fundamental.utils.pinyin import spm
from camel.fundamental.utils.timeutils import timestamp_to_str,get_across_days
from tracer import TraceService
from vehicle import VehicleObject
from base import VehicleStatus
from buffer import MovableObjectBuffer
from map import isPtInRect



class UserQuery(object):
    def __init__(self,user):
        self.user = user  # AccessUser

    def getVehicleHotSpots(self,scale,rect,limit=20):
        """获取指定缩放比时显示的车辆热点图

        :param scale_level:
        :param max: return limited num
        :return:
            {   lon,lat,
                status:{run: 1,stop:2,offline:3},
                scale_level: 20,
                cell_size: 0.1x0.1
            }
        """


        mapgrid = TraceService.instance().getMapGridByScaleLevel(scale)
        if not mapgrid:
            return []

        cells = mapgrid.getCells(rect)     #可视区域的 grid
        # cells = mapgrid.cells.values() # 得到所有网格
        spots = []

        for cell in cells:
            running = 0
            stopped = 0
            offline = 0

            for mo in cell.mos.values():
                if not self.user.getObjects().has_key(mo.getId()):
                    continue # 过滤非用户车辆
                vo = VehicleObject(mo)
                if vo.getStatus() == VehicleStatus.RUNNING:
                    running += 1
                if vo.getStatus() == VehicleStatus.STOPPED:
                    stopped +=1
                if vo.getStatus() == VehicleStatus.OFFLINE:
                    offline+=1
            if running or stopped or offline:
                x,y = cell.center()
                mo = cell.mos.values()[0]
                x,y = mo.getLocation().lon,mo.getLocation().lat
                spots.append({
                    'id': cell.index(),
                    'lon':x,
                    'lat':y,
                    'all': running + stopped + offline,
                    'running':running,
                    'stopped':stopped,
                    'offline':offline,
                    'scale':scale,
                    'cellsize':cell.size()
                })

        #sorted it 根在线运输数从大到小降序
        # spots = sorted(spots,lambda x,y:cmp(x['running']+x['stopped']+x['offline'],y['running']+y['stopped']+y['offline']))
        spots = sorted(spots,lambda x,y:cmp(x['all'],y['all']),reverse=True)
        return spots[:limit]

    def getVehicleStatistics(self):
        """
        获取全网车辆状态统计
        用户所属的车辆不一定采集到数据，对于没有定位记录的车辆属于offline数量
        有定位数据，但时间超过 1小时的也属于offline数量
        :return:
            { all,running,stopped,offline }
        """
        mapgrid = TraceService.instance().getMapGridByMaxScaleLevel()
        cells = mapgrid.cells.values()  # 得到所有网格
        running = 0
        stopped = 0
        offline = 0
        for cell in cells:
            for mo in cell.mos.values():
                if not self.user.getObjects().has_key(mo.getId()):
                    continue # 过滤非用户车辆
                vo = VehicleObject(mo)
                if vo.getStatus() == VehicleStatus.RUNNING:
                    running += 1
                if vo.getStatus() == VehicleStatus.STOPPED:
                    stopped += 1
                if vo.getStatus() == VehicleStatus.OFFLINE:
                    offline += 1

        all = len(self.user.getObjects())
        return {
            # 'all': running+stopped+offline,
            'all': all,
            'running':running,
            'stopped':stopped,
            'offline': all - running - stopped
        }

    # def filterNames(self,name,provider=TypeBase.UNKNOWN.value,status=TypeBase.UNKNOWN.value,limit=20):
    #     """
    #     根据车牌模糊查询车辆
    #     :param id: 车牌名称用于模糊匹配
    #     :param provider: 设备供应商类型
    #     :param status: 车辆运行状态
    #     :param limit: 返回记录数
    #     :return:
    #         []
    #     """
    #     from buffer import MovableObjectBuffer
    #     buff = MovableObjectBuffer.instance()
    #     return buff.filterName(name,limit)


    def filterVechileNames(self,keyword,limit=20):
        """检索车辆名称"""
        result =[]
        # 控制检索用户所属车牌数量
        def _resultBack(id,result):
            if self.user.getObjects().has_key(id) and len(result)<limit:
                result.append(id)
        MovableObjectBuffer.instance().filterNames(keyword,result,_resultBack)
        return result

    def dump_grid(self,grid):
        count =0
        for index,cell in grid.cells.items():
            if len(cell.mos):
                count+=len(cell.mos)
                print "grid:",grid.name," dumps:",cell.index(), "mos:",len(cell.mos)
        print 'total mos:',count,' grid:',grid.name

    def getVehicleByViewRect(self,scale,rect,provider=TypeBase.UNKNOWN.value,status=TypeBase.UNKNOWN.value,limit=500):
        """
        地图画框搜索车辆
        返回车辆名称排序

        :param rect: (x,y,w,h)
        :param provider:
        :param status:
        :param limit:
        :return:
        """
        result = []
        grid = TraceService.instance().getMapGridByScaleLevel(scale)
        if not grid:
            return []
        # self.dump_grid(grid)
        cells = grid.getCells(rect)

        objects = self.user.getObjects()
        for cell in cells:
            # print "grid:", grid.name, " dumps:", cell.index(), "mos:", len(cell.mos)
            # print 'view-rect:',rect,'cell-rect:',cell.rect()
            # print cell.mos
            # for mo in cell.mos.values():
            #     x, y = mo.getLocation().lon, mo.getLocation().lat
            #     print 'view-rect:',rect[0],rect[1],rect[0]+rect[2],rect[1]+rect[3],'cell-rect:', cell.rect()
            #     print mo.getId(),x,y
            #     print 'mo in viewrect:', isPtInRect(rect,(x,y))

            cell.spatialQueryByRect(rect,result,lambda _: objects.has_key( _.getId() ) )

            if len(result) > limit: # 防止查询数量过大
                break

        # sort 车牌排序
        mos = sorted(result,lambda x,y:cmp( spm(x.getId()),spm(y.getId())))
        if status!= TypeBase.UNKNOWN.value:
            mos = filter(lambda _:VehicleObject(_).getStatus()==status,mos)

        result = map(lambda _:VehicleObject(_).dict(),mos)[:limit]
        return result

    def getVehicleByViewCircle(self,scale,circle,provider=TypeBase.UNKNOWN.value,status=TypeBase.UNKNOWN.value,limit=500):
        """
        地图画框搜索车辆
        返回车辆名称排序

        :param circle: (x,y,r)
        :param provider:
        :param status:
        :param limit:
        :return:
        """
        # grid = TraceService.instance().getMapGridByMinScaleLevel()
        grid = TraceService.instance().getMapGridByScaleLevel(scale)
        if not grid:
            return []
        cx,cy,radius = circle
        rect = (cx - radius, cy - radius, radius * 2, radius * 2)
        objects = self.user.getObjects()
        cells = grid.getCells(rect)
        result=[]
        for cell in cells:
            cell.spatialQueryByCircle(circle,result,lambda _: objects.has_key( _.getId() ))
            if len(result) > limit: # 防止查询数量过大
                break

        # sort 车牌排序
        mos = sorted(result,lambda x,y:cmp( spm(x.getId()),spm(y.getId())) )
        if status!= TypeBase.UNKNOWN.value:
            mos = filter(lambda _:VehicleObject(_).getStatus()==status,mos)

        result = map(lambda _:VehicleObject(_).dict(),mos)[:limit]
        return result

    def getVehicleWithIDs(self,ids):
        """
        根据传入的车辆标识查询车辆当前位置状态
        ids 为空则返回所有车辆
        :param ids:
        :type ids:list
        :return:
            []
        """
        buffer = TraceService.instance().getBuffer()
        result =[]
        objects = self.user.getObjects()
        ids_ar = []
        if ids:
            for _  in ids:
                if objects.has_key(_):
                    ids_ar.append(_)
        else:
            ids_ar = objects.keys()
        for id in ids_ar:
            mo = buffer.get(id)
            if mo:
                result.append(mo)
        result = map(lambda _: VehicleObject(_).dict(), result)
        return result

    def getVehicleTrack(self,id,start,end,granule):
        """查询车辆轨迹
        CREATE TABLE public.mo_data_20170501 (
          id CHARACTER VARYING(20) NOT NULL,
          time INTEGER NOT NULL,
          data JSONB,
          last JSONB,
          PRIMARY KEY (id, time)
        );
        CREATE INDEX mo_data_20170501_id_index ON mo_data_20170501 USING BTREE (id);
        CREATE INDEX mo_data_20170501_time_index ON mo_data_20170501 USING BTREE (time);
        CREATE INDEX mo_data_20170501_time_id_index ON mo_data_20170501 USING BTREE (id, time);

            注意： 查询跨表
        """
        days = get_across_days(start,end)
        result =[]
        for day in days:
            y,m,d = day.year,day.month,day.day
            table = "mo_data_" + "%04d%02d%02d"%(y,m,d)

            # 获得全部轨迹记录，不做数据颗粒处理
            sql = "select data from {table} where id=%s and (time BETWEEN %s and %s) order by time".format(table=table)

            conn = TraceService.instance().getDatabaseConnection()
            try:
                cur = conn.cursor()
                cur.execute(sql,(id,start,end))

                last_time =0
                row = cur.fetchone()
                while row:
                    # for data in json.loads(row[0]):
                    # data = row[0]
                    # if granule>5:
                    #     granule = 5
                    # num = len(row[0])//granule

                    for _ in row[0]:

                        step = VehicleObject(MovableObject.unmarshall(_)).dict()
                        if step['time'] - granule*60 > last_time:
                            last_time = step['time']
                            result.append(step)

                    # for _ in row[0]:
                    #     step = VehicleObject(MovableObject.unmarshall(_)).dict()
                    #     result.append(step)
                    row = cur.fetchone()
            finally:
                TraceService.instance().freeDatabaseConnection(conn)

        return result

