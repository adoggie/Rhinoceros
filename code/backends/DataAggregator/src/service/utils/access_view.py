#coding:utf-8

import uuid
from camel.fundamental.utils.useful import Singleton
from map import isPtInRect
from tracer import TraceService

class MapAccessSession(object):
    def __init__(self,scale,viewrect):
        self.session = uuid.uuid4().hex
        self.scale = scale
        self.viewrect = viewrect
        self.mos ={}        #当前地图可视区域内的车辆
        self.forward_mos={} #向前端用户推送车辆
        self.initData()

    def initData(self):
        """
        加载当前可视区域的所有车辆
        :return:
        """
        rect = self.viewrect
        grid = TraceService.instance().getMapGridByMinScaleLevel()
        cells = grid.getCells(rect)
        result = []
        for cell in cells:
            cell.spatialQueryByRect(rect, result)


    def update(self,mo):
        """
        检测mo进入或者离开当前视图区域
        :param mo:
        :return:
        """
        loc = mo.getLocation()
        if isPtInRect(self.viewrect,(loc.lon,loc.lat)):
            if not self.mos.has_key(mo.getId()):
                self.forward_mos[mo.getId()] = mo
            else: # 判断是否有差异
                current = self.mos[mo.getId()]
                if current.getLocation().unique()!=mo.getLocation().unique():
                    self.forward_mos[mo.getId()] = mo
            self.mos[mo.getId()] = mo
        else:
            del self.mos[mo.getId()] #从当前视野中剔除

    def data(self):
        return {
            'vehicles':[],
            'access_session':self.session
        }

    @staticmethod
    def null():
        return MapAccessSession().data()


class MapAccessManager(Singleton):
    def __init__(self):
        pass
