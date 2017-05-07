#coding:utf-8

import time
from camel.rhinoceros.base import MovableObject
from base import  VehicleStatus,OFFLINE_TIME

class VehicleObject(object):
    def __init__(self,mo):
        self.mo = mo

    def getStatus(self):
        if time.time() - self.mo.getLocation().time > OFFLINE_TIME:
            return VehicleStatus.OFFLINE

        if self.mo.getLocation().speed != 0:
            status = VehicleStatus.RUNNING
        else:
            status = VehicleStatus.STOPPED
        return status

    def dict(self):

        result = self.mo.getLocation().dict()
        result['id'] = result['moid']

        # content = self.mo.dict()
        result['status'] = self.getStatus()
        result['extra'] ={}
        return result
