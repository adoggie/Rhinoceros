#coding:utf-8

import os
import time
import gevent
import requests
import json

from camel.fundamental.utils.timeutils import timestamp_to_str
from camel.fundamental.application.app import Application,instance
from camel.fundamental.amqp import AmqpManager
from camel.rhinoceros.base import  DataCategory
from service.buffer import MovableObjectBuffer

class AdapterBase(object):
    def __init__(self,cfgs):
        self.cfgs = cfgs
        self.vehicles = []
        self.started = False
        self.task = None
        self.batch_taskes=[]

        self.buffer = MovableObjectBuffer(cfgs.get('name'))

        self.dbg_req_num = 0
        self.dbg_resp_num = 0

        self.count = 0
        self.excluded = []  #排除车辆
        self.time_twisters = {} #时间扭曲 { id: distance }

    @property
    def name(self):
        self.cfgs.get('name')

    @property
    def enable(self):
        self.cfgs.get('enable')


    def _loadVehicles(self):
        vehicles_file = os.path.join(instance.getDataPath(), self.cfgs.get('vehicle_list'))
        fp = open(vehicles_file)
        for line in fp.readlines():
            line = line.strip()
            if not line:
                break
            self.vehicles.append(line.decode('utf-8'))

    def _init(self):

        path = os.path.join(instance.getLogPath(), '%s_timetwiste_vehicles.txt' % self.cfgs.get('name'))
        if os.path.exists(path):
            os.unlink(path)

        self._loadVehicles()



    def open(self):
        self._init()
        self.task = gevent.spawn(self._task_exec)
        # self.doRequest()
        # self._request_getLocation([u'浙A2K900']) # G7
        # self._request_getLocation( [u'粤AV4146'] ) # G7
        # self._request_getLocation(u'陕YH0009') # ZJXL

        return True

    def close(self):
        self.started = False
        gevent.joinall([self.task])


    @property
    def freq(self):
        return self.cfgs.get('request_freq',60)


    def __relist_vehicles(self):
        """重新整理车辆列表"""
        for _ in self.excluded:
            if self.vehicles.count(_):
                self.vehicles.remove(_)
        self.excluded = []

        for _,v in self.time_twisters.items():
            if self.vehicles.count(_):
                self.vehicles.remove(_)

        self.time_twisters = {}

    def relist_vehicles(self):
        #记录时间扭曲的机器
        if self.time_twisters:
            path = os.path.join(instance.getLogPath(), '%s_timetwiste_vehicles.txt' % self.cfgs.get('name'))
            fp = open(path, 'a')
            fp.write("vehicles num:%s\n" % len(self.time_twisters))
            for k,v in self.time_twisters.items():
                fp.write("%s , systime:%s , gpstime: %s ,  distance:%s minutes,\n"%
                    (k.encode('utf-8'),
                    v.get('sys_time'),
                    v.get('gps_time'),
                    v.get('distance')))
            fp.close()

        # 记录无效的请求车辆列表
        if self.excluded:
            path = os.path.join(instance.getLogPath(), '%s_exclude_vehicles.txt' % self.cfgs.get('name'))
            fp = open(path, 'w')
            fp.write("vehicles num:%s\n" % len(self.excluded))
            for _ in self.excluded:
                fp.write(_.encode('utf-8'))
                fp.write('\n')
            fp.close()

        self.__relist_vehicles()

        #记录最新有效的请求车辆列表
        path = os.path.join( instance.getLogPath(),'%s_vehicles.txt'%self.cfgs.get('name'))
        fp = open(path,'w')
        fp.write("vehicles num:%s\n"%len(self.vehicles))
        for _ in self.vehicles:
            fp.write( _.encode('utf-8'))
            fp.write('\n')
        fp.close()

    def doRequest(self):

        self.relist_vehicles()

        pagination = self.cfgs.get('pagination',0)
        if pagination == 0 :
            pagination = 99999999999

        self.batch_taskes = []
        batches = []
        if len(self.vehicles) > pagination:
            a = range(0,len(self.vehicles),pagination)
            b = map(lambda x:x+pagination,a)
            ab = zip(a,b)
            batches = ab
        else:
            batches=[[0,len(self.vehicles)]]

        self._batch_start()
        for batch in batches:
            vehicles = self.vehicles[batch[0]:batch[1]]
            self.batch_taskes.append(self.doBatchRequest(vehicles))
            self._batch_request_wait()

    def _batch_request_wait(self):
        return self.cfgs.get('batch_req_wait',0.5)

    def _batch_start(self):
        self.dbg_resp_num = 0
        self.dbg_resp_num = 0


    def __doBatchRequest(self,vehicles):
        tasks =[]
        for ve in vehicles:
            # params = self._makeRequestData_getLocation(ve)
            let = gevent.spawn(self._request_getLocation, ve)
            tasks.append(let)
        return tasks

    def doBatchRequest(self,vehicles):
        tasklet = gevent.spawn(self._request_getLocation, vehicles)
        return tasklet



    def _task_exec(self):
        self.started = True
        while self.started:
            self.doRequest()
            gevent.joinall(self.batch_taskes)
            gevent.sleep( self.freq)
            if not self._repeated():
                break

    def  _repeated(self):
        return True

    def format_ymdhms(self):
        import datetime
        dt = datetime.datetime.now()
        return "%04d-%02d-%02d %02d:%02d:%02d" % (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    def _request_getLocation(self,vehicles):
        """请求车辆实时位置"""
        pass


    def _makeRequestParams_getLocation(self,vehicle_id):pass

    def _makeSign(self, params):pass


    def _time_twiste(self,loc):
        """时间扭曲不通过返回None"""

        enable = self.cfgs.get('timetwiste_enable',False)
        if not enable:
            return loc
        distance = self.cfgs.get('timetwiste_distance',60)*60
        safe_time = time.time() - distance, time.time()

        if loc.time < safe_time[0] or loc.time > safe_time[1]:
            instance.getLogger().warning(
                u'<%s> getLocation error. vehicle:%s , gps 时间扭曲:%s' %
                (self.cfgs.get('name').upper(),loc.getId(), timestamp_to_str(loc.time)))
            self.time_twisters[loc.getId()] = {
                'distance':int((time.time() - loc.time)/60.) , #记录扭曲时长
                'sys_time':timestamp_to_str(time.time()),
                'gps_time':timestamp_to_str(loc.time)
            }
            return None
        return loc


    def _onDataReady(self,vehicle_id,data):
        """数据接收完成之后进行下一步消息的投递
        """


        data = self._time_twiste(data)
        if not data:
            return
        # return data

        data = self.buffer.enqueue(vehicle_id,data)
        if data: # fresh data
            env = data.toEnvelope()  # 发送 DataEnvelope
            name = self.cfgs.get('post_mq')
            serial = env.marshall()
            print serial
            tick =   timestamp_to_str(env.payloads.get(DataCategory.LOC.value).time, fmt='%Y%m%d_%H%M%S')


            print env.getId(),tick
            self.count+=1
            print 'data sent:',self.count
            mq = AmqpManager.instance().getMessageQueue(name)
            mq.produce( serial )
