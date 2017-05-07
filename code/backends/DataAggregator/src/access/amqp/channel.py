#coding:utf-8

"""
收集车辆定位数据
"""
import traceback
from camel.fundamental.application.app import instance
from service.accumulate import Accumulator

def data_entry(data):
    try:
        Accumulator.instance().onDataRecieved(data)
    except:
        traceback.print_exc()
        instance.getLogger().warning( data )
        instance.getLogger().warning(traceback.format_exc())


