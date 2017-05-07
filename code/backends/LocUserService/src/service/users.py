#coding:utf-8

import os
import os.path
import traceback
import string

from camel.fundamental.cache.manager import CacheManager
from camel.fundamental.application.app import Singleton,instance
from camel.rhinoceros.token import encode_user_token
from camel.rhinoceros.errors import ErrorDefs
from camel.rhinoceros.webapi import CallReturn,ErrorReturn

class UserManager(Singleton):
    def __init__(self):
        self.cfgs = None

    def init(self,cfgs):
        self.cfgs = cfgs


    def getVehicles(self,user):
        """
        根据用户名获取车辆列表
        :param user:
        :return:
        """
        data_path = instance.getDataPath()
        ids = []
        for _ in self.cfgs.get('users',[]):
            if _.get('name') == user:
                files = _.get('vehicle',[])
                for f in files:
                    path = os.path.join(data_path,f)
                    lines = open(path).readlines()
                    lines = map(string.strip,lines)
                    for line in lines:
                        if not line: continue
                        ids.append(line)
        return ids

    def authenticate(self,app_id,secret_key,user_id):
        if self.cfgs.get('app_id') != app_id or self.cfgs.get('secret_key') !=secret_key:
            return ErrorReturn(ErrorDefs.ApplicationAuthorizeError)

        cache = CacheManager.instance().get()
        data = {
            'app_id':app_id,
            'secret_key':secret_key,
            'user_id':user_id
        }
        token = encode_user_token(data)
        #将用户归属的车辆放入redis
        ids = self.getVehicles(user_id)
        key = '{user_id}$$vehicles'.format(user_id=user_id)
        cache.delete(key)
        cache.h.sadd(key,*ids)
        return CallReturn(result=token)

