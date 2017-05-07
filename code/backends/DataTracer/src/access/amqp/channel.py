#coding:utf-8

"""
收集车辆定位数据
"""

from service.tracer import TraceService

def data_entry(data):
    TraceService.instance().onDataRecieved(data)


