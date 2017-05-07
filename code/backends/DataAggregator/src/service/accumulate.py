#coding:utf-8

"""
采集的数据每隔5分钟被分块存储

每个mo的数据在间隔5分钟内被写入同一个数据文件

"""
import time
import os
import os.path
import base64
import string
import shutil
import gevent
import json
from camel.fundamental.application.app import instance
from camel.fundamental.utils.timeutils import timestamp_to_str
from camel.fundamental.utils.useful import Singleton
from camel.rhinoceros.base import  DataEnvelope,MovableObject
from persistence import PersistenceManager


class Accumulator(Singleton):
    def __init__(self):
        self.cfgs = None
        self.count = 0

    def init(self,cfgs):
        self.cfgs = cfgs
        PersistenceManager.instance().init(self.cfgs.get('persistence'))
        gevent.spawn(self._thread_persist)

        # self._thread_persist()

    def getCacheFileName(self,mo):

        span = self.cfgs.get('data_span',5)*60
        loc = mo.getLocation()
        print mo.getId(),loc.time, timestamp_to_str(loc.time, fmt='%Y%m%d_%H%M%M')
        start = (loc.time//span)*span
        name = timestamp_to_str(start,fmt='%Y%m%d_%H%M')
        app_data_path = instance.getDataPath()

        path = os.path.join(app_data_path,self.cfgs.get('data_path'),name)
        if not os.path.exists(path):
            os.makedirs(path)
        filename = mo.getId().encode('utf-8')+'.txt'
        return os.path.join(path,filename)

    def onDataRecieved(self,data):
        env = DataEnvelope.unmarshall(data)
        if env:
            mo = env.toMovableObject()
        else:
            print 'data dirty skipped..'
            return
        self.count+=1

        print "data recved :",self.count
        path =  self.getCacheFileName(mo)
        fp = open(path,'a')
        fp.write(mo.marshall())
        fp.write("\n")
        fp.close()

    def _thread_persist(self):
        """
        将缓存数据持久化

        1.数据校验，保证缓存的记录没有超出时间边界，并保证按时间排序
        2.扫描时间从 1天前 - 距今两个缓存时间跨度
        :return:
        """
        seconds_oneday = 3600*24
        span = self.cfgs.get('data_span')*60
        distance = self.cfgs.get('distance') * span
        app_data_path = instance.getDataPath()
        cache_path = os.path.join(app_data_path, self.cfgs.get('data_path'))
        back_path = os.path.join(app_data_path, self.cfgs.get('backup_path'))
        if not os.path.exists(back_path):
            os.makedirs(back_path)
        while True:
            now = time.time()
            end = (now//span)*span - distance
            start = end - seconds_oneday
            while start<= end:
                name = timestamp_to_str(start, fmt='%Y%m%d_%H%M')
                path = os.path.join( cache_path, name)
                # print path
                if not os.path.exists(path):
                    start += span
                    continue

                for _ in os.listdir(path):
                    if _.find('.txt') == -1:
                        continue
                    self.processFile( start,span,os.path.join(path,_))
                # 将数据目录移到备份目录
                src = path
                dest = os.path.join(back_path,name)
                print 'src:',src
                print 'dest:',dest
                if os.path.exists(dest):
                    shutil.rmtree(dest)

                shutil.move(src, dest)

                start+=span

            gevent.sleep(5)

    def processFile(self,start,span,locfile):
        """
        排序、时间范围校验
        :param start:
        :param span:
        :param locfile:
        :return:
        """
        lines =  open(locfile).readlines()
        lines = map(string.strip,lines)
        list = map(json.loads,lines)
        mos = []
        for _ in list:
            mo = MovableObject.unmarshall(_)
            if not mo:
                continue
            loc = mo.getLocation()
            if loc.time < start or loc.time > start+span:
                instance.getLogger().warning('location time is not in (%s,%s)'%(start,start+span))
                continue
            mos.append(mo)

        #根据时间排序
        mos = sorted(mos, lambda x, y: cmp(x.getLocation().time, y.getLocation().time))
        PersistenceManager.instance().write(start,span,mos)



