#coding:utf-8

"""
收集车辆定位数据
"""

from service.shuffler import ShuffleService

def data_entry(data):
    ShuffleService.instance().onDataRecieved(data)


