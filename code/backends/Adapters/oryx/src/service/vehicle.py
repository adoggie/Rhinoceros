#coding:utf-8

from  camel.rhinoceros.base import YES,NO,MovableObject

class VehicleObject(MovableObject):
    """车辆对象用于保存最新的监控数据
    :param datas:
    :type datas:dict { PayloadType: DataCategory }
    """
    def __init__(self,vehicle_id):
        MovableObject.__init__(self,vehicle_id)
