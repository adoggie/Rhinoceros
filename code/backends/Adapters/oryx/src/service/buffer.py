#coding:utf-8

from camel.rhinoceros.base import DataCategory,MovableObject,YES,NO

class MovableObjectBuffer(object):
    """数据缓冲池
    每一个对接adapter都有对应的一个数据接收缓冲区，成为slot.
    slot中保存最新的车辆数据，在主动向外请求(http-request)的场景下，由于定时执行
    的请求会获取相同的数据，slot用于识别最新数据,防止被重复提交
    """
    def __init__(self,name):
        self.name = name
        self.mos = {}  # {plate: obj (VehicleObject) }

    def enqueue(self,mo_id,data):
        """
        :param data:
        :type data: DataCategory
        :return:
        """
        mo = self.mos.get(mo_id)
        if not mo:
            mo = MovableObject(mo_id)
            self.mos[mo_id] = mo
        if mo.update(data) == YES:
            return data
        return None

    def dequeue(self):
        pass