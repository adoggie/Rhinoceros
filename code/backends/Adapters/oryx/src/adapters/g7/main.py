#coding:utf-8


"""
签名验证工具
http://114.215.193.157/sign/

unicode转换
http://www.bejson.com/convert/unicode_chinese/
"""
import os.path
import hashlib
import json
import gevent
import requests
import time

from camel.fundamental.application.app import instance
from camel.fundamental.utils.timeutils import str_to_timestamp
from ..adapter import AdapterBase
from camel.rhinoceros.base import LocationData,ProviderType,LocationEncodeType


class AdapterG7(AdapterBase):
    def __init__(self,cfgs):
        AdapterBase.__init__(self,cfgs)


    def _makeRequestParams_getLocation(self,vehicles):

        carnums = ','.join(vehicles)
        time = self.format_ymdhms()
        transaddr =  3

        query_params = {'carnum': carnums, 'isbind': 1,
            'transaddr': transaddr,'geotype':1}
        # query_params ={"carnum":"粤AV4146"}

        # s = json.dumps(query_params)
        # print s
        # sign = self._makeSign( query_params )
        sign =''
        data = query_params

        data = json.dumps(data, sort_keys=True, separators=(',', ':'))

        payload = {
            'method':'truck.device.getTruckAddress',
            'timestamp':self.format_ymdhms(),
            'app_key': self.cfgs.get('account'),
            'sign':sign,
            'data':data
        }
        # payload['timestamp'] = '2017-04-22 10:31:09'
        sign = self._makeSign(payload)
        payload['sign'] = sign
        # payload = json.dumps(payload)
        return payload

    def _makeSign(self,params):
        screct_key = self.cfgs.get('password')
        # body = json.dumps(params['data'],sort_keys=True,separators=(',',':'))
        data = '%sapp_key%sdata%smethod%stimestamp%s%s'%(screct_key,
            params['app_key'],params['data'],
            params['method'],params['timestamp'],
            screct_key)

        # print data
        # print body
        md = hashlib.md5()
        md.update( data )
        sign = md.hexdigest().upper()
        # print sign
        return sign

    def _repeated(self):
        return True

    def _request_getLocation(self,vehicles):
        """微线程执行 车辆位置信息的请求获取

        :param vehicle_id:  车辆标识码 或者 车牌
        :return:
        """
        params = self._makeRequestParams_getLocation(vehicles)
        url = self.cfgs.get('access_url')
        resp = requests.post(url, data=params)
        content = resp.json()
        if content.get('code',-1) !=0:  # 0: okay else false
            return
        records = content.get('data',[])

        self.dbg_req_num += len(vehicles)

        for data in records:
            code = data.get('code',-1)
            if  code !=0:
                instance.getLogger().warning('<G7> getLocation error. code:%s , vehicle:%s message:%s'%(data.get('code'),data.get('carnum',''),data.get('message')))
                if code == 9  : # 车辆未绑定设备???
                    self.excluded.append(data.get('carnum',''))
                continue
            vehicle_id = data.get('carnum')
            loc = LocationData( vehicle_id)  # spawn location point
            loc.version = '0.1'
            loc.provider = ProviderType.G7.value
            loc.lon = data.get('lng',0)
            loc.lat = data.get('lat',0)
            loc.speed = data.get('speed',0)
            loc.direction = data.get('course',0)
            loc.status = 0
            loc.address = data.get('address','')
            loc.text = data.get('status',0)
            loc.encode = LocationEncodeType.BD.value
            loc.time = str_to_timestamp( data.get('time','') ) # todo. format timestamp
            loc.extra['orgcode'] = data.get('orgcode','')   #	机构号
            loc.extra['fromtype'] = data.get('fromtype','') # 车辆类型 1为自建车辆，3为外部共享车辆
            loc.extra['address'] = data.get('address','')
            loc.extra['status'] = data.get('status','')
            loc.extra['offline'] = data.get('offline',0)        # 离线持续时间(s)
            loc.extra['offline_start'] = data.get('movetime')   # 离线开始时间

            print loc.dict()


            print 'batch request num:', self.dbg_req_num
            self.dbg_resp_num += 1
            print  'recieved locations num:', self.dbg_resp_num



            self._onDataReady( vehicle_id,loc )

    def open(self):
        self._init()
        self.task = gevent.spawn(self._task_exec)
        # self.doBatchRequest(self.vehicles)
        # self._request_getLocation(self.vehicles)

    # def _batch_request_wait(self):
    #     gevent.sleep(0.02)
