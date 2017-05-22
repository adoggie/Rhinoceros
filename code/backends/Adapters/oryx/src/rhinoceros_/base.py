#coding:utf-8

import json
from camel.fundamental.basetype import ValueEntry


YES = 1
NO = 2

class TypeBase(object):
    UNKNOWN = ValueEntry(0, u'')

class ProviderType(TypeBase):
    G7      = ValueEntry(1,u'G7')
    ZJXL    = ValueEntry(2,u'中交兴路')
    YL      = ValueEntry(3,u'易流')
    ZQ      = ValueEntry(4,u'重汽')

class PayloadType(TypeBase):
    LOC     = ValueEntry(0x01,u'位置信息')
    EMS     = ValueEntry(0x02,u'发送机数据')
    ETC     = ValueEntry(0x04,u'ETC数据')

class LocationDeviceType(TypeBase):
    GPS     = ValueEntry(1,u'GPS定位数据')
    BD      = ValueEntry(2,u'北斗定位数据')

class LocationNeedFix(TypeBase):
    YES = ValueEntry(1,u'yes')
    NO = ValueEntry(2,u'no')

class LocationEncodeType(TypeBase):
    WGS84   = ValueEntry(1,u'GPS')
    GCJ     = ValueEntry(2,u'国测局')
    BD      = ValueEntry(3,u'百度坐标')

class DataCategory(TypeBase):
    LOC = ValueEntry(1<<0, u'位置信息')
    EMS = ValueEntry(1<<1, u'发送机数据')
    ETC = ValueEntry(1<<2, u'ETC数据')

    def __init__(self,type_,version=1,provider = TypeBase.UNKNOWN.value):
        self.type = type_
        self.version = version  # 版本
        self.provider = provider    #供应商
        self.sys_time = 0       #系统时间


    def unique(self):
        return 0

    def dict(self):
        return self.hash_object()

    def json(self):
        return json.dumps(self.dict())

    def hash_object(self):
        obj = self
        attrs = [s for s in dir(obj) if not s.startswith('__')]
        kvs = {}
        for k in attrs:
            attr = getattr(obj, k)
            if not callable(attr) and not isinstance(attr,ValueEntry):
                kvs[k] = attr
        return kvs

    def toEnvelope(self):
        env = DataEnvelope(self.provider)
        env.add(self)
        return env

class LocationData(DataCategory):
    """位置数据"""
    def __init__(self,vehicle,lon=0.0,lat=0.0,speed=0.0,direction=0.0,
        time=0,altitute=0.0,encode=LocationEncodeType.WGS84.value):
        DataCategory.__init__(self,DataCategory.LOC.value)

        self.vehicle = vehicle
        self.lon = lon
        self.lat = lat
        self.speed = speed
        self.direction = direction
        self.time = time
        self.altitute = altitute
        self.encode = encode                        # 位置点编码类型  默认wgs84
        self.need_fix = LocationNeedFix.NO.value    # 无需修正

        self.extra = {

        }

    def unique(self):
        return self.time


class EMS_Data( DataCategory ):
    """发送机采集数据"""
    def __init__(self,vehicle):
        DataCategory.__init__(self,DataCategory.EMS)
        self.vehicle = vehicle

    def unique(self):
        return 0

class DataEnvelope(object):
    """
    :param version
    :type version float
    :param provider 设备供应商类型
    :type provider DataProviderType
    """
    def __init__(self,provider=''):
        self.provider = provider
        self.payloads={}

    @property
    def payload_mask(self):
        mask = 0
        for _ in self.payloads.values():
            mask |= _.type
        return mask

    def add(self,data):
        self.payloads[data.type] = data
        return self

    def dict(self):

        whole = {
            'provider':self.provider,
            'mask': self.payload_mask,
            'data': [ _.dict() for _ in self.payloads.values() ]
        }
        return whole

    def hash_object(self):
        obj = self
        attrs = [s for s in dir(obj) if not s.startswith('__')]
        kvs = {}
        for k in attrs:
            attr = getattr(obj, k)
            if not callable(attr):
                kvs[k] = attr
        return kvs

    def json(self):
        return json.dumps(self.dict())


"""
1.为了同时接入大规模数量的车辆数据，根据车牌将车辆hash分割到不同接入分区，
分区服务器在发起并行的查询请求


"""