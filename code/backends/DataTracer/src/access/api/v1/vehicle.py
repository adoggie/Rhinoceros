#coding:utf-8

import json
import datetime
import time

from flask import request,g
from service.buffer import MovableObjectBuffer
from camel.rhinoceros.webapi import CallReturn,ErrorReturn,ErrorDefs
from service.access_user import AccessUserManager
from service.decorator import user_access_check
from service.tracer import TraceService

"""
1. 获取指定车辆名称的位置信息(支持多车辆)
2. 查询指定车辆名称的历史位置信息
3.

"""

@user_access_check
def get_vehicle_names():
    """查询车辆"""
    keyword = request.values.get('name')
    if not keyword:
        return ErrorReturn(ErrorDefs.ParameterIllegal).response
    limit =request.values.get('limit',20)
    limit = int(limit)
    query = g.user.getQuery()
    mos = query.filterVechileNames(keyword,limit)
    return CallReturn(result=mos).response

@user_access_check
def get_vehicles_statistics():
    """统计车辆运行状态"""
    query = g.user.getQuery()
    data = query.getVehicleStatistics()
    return CallReturn(result=data).response


@user_access_check
def get_vehicle_hotspots():

    scale = int(request.values.get('scale'))
    rect = request.values.get('rect','')
    if rect:
        rect = map(float,rect.split(','))
    limit = int(request.values.get('limit',20))
    query = g.user.getQuery()
    data = query.getVehicleHotSpots(scale,rect,limit)
    return CallReturn(result=data).response

@user_access_check
def get_vehicles_by_geometry():
    """根据地理视野查询车辆位置

    :param scale
    :param rect
    :param circle
    :param limit
    :return:
    """
    scale = int(request.values.get('scale'))
    rect = request.values.get('rect', '')
    if rect:
        rect = map(float, rect.split(','))
    circle = request.values.get('circle','')
    if circle:
        circle = map(float,circle.split(','))

    limit = int(request.values.get('limit', 20))
    query = g.user.getQuery()
    data =[]
    if rect:
        data = query.getVehicleByViewRect(scale,rect,limit=limit)
    if circle:
        data = query.getVehicleByViewCircle(scale,circle,limit=limit)
    return CallReturn(result=data).response

@user_access_check
def get_vehicle_position():
    """查询车辆定位数据"""
    ids = request.values.get('ids', '')
    ids = filter(lambda x: x!='',ids.split(','))
    query = g.user.getQuery()
    data = query.getVehicleWithIDs(ids)
    return CallReturn(result=data).response

@user_access_check
def get_vehicle_track():
    """
    查询车辆运行轨迹
    :return:
    """
    id = request.values.get('id','')
    start = request.values.get('start')
    end = request.values.get('end')
    granule = request.values.get('granule',0)
    start = int(float(start))
    if not end:
        end = time.time()
    end = int(float(end))
    granule = int(granule)
    if granule < 0 : granule = 0
    if granule > 20: granule = 20
    if not id :
        return ErrorReturn(ErrorDefs.ParameterIllegal).response

    s = datetime.datetime.fromtimestamp(start)
    e = datetime.datetime.fromtimestamp(end)
    # days = e.date() - s.date()

    max_duration = TraceService.instance().cfgs.get('query_track',{}).get('max_duration',24)

    if (s - e).seconds > max_duration*3600 :
        return ErrorReturn(ErrorDefs.ParameterIllegal,errmsg=u'查询时间超限(%s hours)'%max_duration).json

    query = g.user.getQuery()
    data = query.getVehicleTrack(id,start,end,granule)

    return CallReturn(result=data).response


