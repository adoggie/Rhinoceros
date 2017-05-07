#coding:utf-8

import time
import gevent
from camel.fundamental.cache.manager import CacheManager
from camel.fundamental.utils.useful import Singleton
from camel.rhinoceros.base import TypeBase
from camel.rhinoceros.token import encode_user_token,decode_user_token

from tracer import TraceService
from vehicle import VehicleObject
from base import VehicleStatus,SpatialQueryGeomType
# from access_view import MapAccessSession,MapAccessManager
from query import UserQuery
from buffer import MovableObjectBuffer

class AccessUser(object):
    def __init__(self,user_id):
        self.user_id = user_id
        self.mos = {}           # 车辆标识列表，并不关联mo对象，hash只为快速判断是否存在
        self.active_time = 0    # 活跃时间
        self.query = UserQuery(self)
        self.delta = None       # 额外的附加数据

        self.init()
        self.update()


    def update(self):
        """保持访问新鲜"""
        self.active_time = time.time()

    def getObjects(self):
        return self.mos

    def getQuery(self):
        return self.query

    def init(self):
        """
        获取用户的车辆数据
        :return:
        """
        self.pull_vehicles()

    def pull_vehicles(self):
        """定时拉取用户的车辆列表"""
        key = "{user_id}$$vehicles".format(user_id=self.user_id)
        cache = CacheManager.instance().get()
        ids = cache.h.smembers(key)
        # redis 存储的数据是utf-8 ，需要转成unicode
        ids = map(lambda _:_.decode('utf-8'),ids)
        for _ in ids:
            if not self.mos.has_key(_):
                self.mos[_] = None



class AccessUserManager(Singleton):
    def __init__(self):
        self.users = {}

    def init(self):
        gevent.spawn(self._thread_user_life)

    def _thread_user_life(self):
        """
        检查登录用户有效存活时间 ， 长时间未访问则删除用户
        :return:
        """
        while True:
            gevent.sleep(60)
            for user in self.users.values():
                user.pull_vehicles()    # 定时拉取车辆列表

    def close(self):
        pass

    def getUser(self,user_id):
        """
        redis 存放用户的信息
            access_key:user-info { yto_user,settings:{} }
            yto_user#vehicles: ['A','B','C']

        locationUserservice 系统在处理用户登陆时，将用户信息和用户所属车辆放入redis

        :param key:
        :return:
        """
        # user_info = decode_user_token(key)
        # user_id = user_info.get('user_id')

        if self.users.has_key( user_id ):
            user = self.users.get( user_id )
        else:
            user = AccessUser(user_id)

        user.update()
        return user

