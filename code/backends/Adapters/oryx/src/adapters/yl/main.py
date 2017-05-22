#coding:utf-8


"""
签名验证工具

unicode转换
http://www.bejson.com/convert/unicode_chinese/
"""
import os.path
import hashlib
import json
import gevent
import requests

from camel.fundamental.application.app import instance
from camel.fundamental.utils.timeutils import str_to_timestamp
from ..adapter import AdapterBase
from camel.rhinoceros.base import LocationData,ProviderType,LocationEncodeType


class AdapterYL(AdapterBase):
    def __init__(self,cfgs):
        AdapterBase.__init__(self,cfgs)

    def open(self):
        self._init()
        self.task = gevent.spawn(self._task_exec)
        # self.doRequest()
        # self._request_getLocation([u'川AJ9930',u'川AJ993x']) # G7
        return True

    def _makeRequestParams_getLocation(self,vehicles):

        carnums = ','.join(vehicles)
        payload = {
            'method':'GetVehcileInfo',
            'timestamp':self.format_ymdhms(),
            'appkey': self.cfgs.get('account'),
            'format':'json',
            # 'vehicle':carnums.encode('utf-8'),
            'vehicle':-1,
            'isoffsetlonlat':2, #百度
            'sessionid':''
        }
        # payload['timestamp'] = '2017-04-22 10:31:09'
        sign = self._makeSign(payload)
        payload['sign'] = sign
        # payload = json.dumps(payload)
        return payload

    def _makeSign(self,params):
        screct_key = self.cfgs.get('password')
        # body = json.dumps(params['data'],sort_keys=True,separators=(',',':'))
        keys = params.keys()
        keys = sorted(keys)
        data = ''.join(map(lambda x:"%s%s"%(x,params[x]),keys))
        data = '%s%s%s'%(screct_key, data,screct_key)

        md = hashlib.md5()
        md.update( data )
        sign = md.hexdigest().upper()

        return sign

    # def _batch_request_wait(self):
    #     gevent.sleep(0.2)

    def _repeated(self):
        return True

    def _request_getLocation(self,vehicles):
        """微线程执行 车辆位置信息的请求获取

        :param vehicle_id:  车辆标识码 或者 车牌
        :return:
        """
        # print vehicles

        # gevent.sleep(0.01)
        params = self._makeRequestParams_getLocation(vehicles)
        url = self.cfgs.get('access_url')
        resp = requests.post(url, data=params)
        content = resp.json()
        result = content.get('result',{})
        code = int(result.get('code',-1))
        if code!=1:  # 0: okay else false
            instance.getLogger().warning(
                'getLocation error. code:%s , message:%s' % (code, result.get('message','')))
            # return
            if code == 42:  # 车辆未绑定设备???
    # 1.多车查询时(接口：GetVehcileInfo)，其中某一台车未绑定，导致此批次请求返回42错误。导致此批次其他车辆数据无法获取
    # 2.请求频率0.2秒，也报ddos攻击
                for  _ in vehicles:
                    self.excluded.append(_)
                return

        records = result.get('data',[])

        self.dbg_req_num+=len(vehicles)
        print 'batch request num:',self.dbg_req_num
        self.dbg_resp_num+=len(records)
        print  'recieved locations num:',self.dbg_resp_num

        for data in records:
            vehicle_id = data.get('Vehicle')
            loc = LocationData( vehicle_id)  # spawn location point
            loc.version = '0.1'
            loc.provider = ProviderType.YL.value
            loc.lon = data.get('Lon',0)
            loc.lat = data.get('Lat',0)

            loc.lat = data.get('Lat02', 0)  # 根据参数isoffsetlonlat返回的纬度
            loc.lon = data.get('Lon02', 0)  # 根据参数isoffsetlonlat返回的纬度

            loc.speed = data.get('Speed',0)
            loc.time = str_to_timestamp( data.get('GPSTime',0) ) # todo. format timestamp
            loc.direction = data.get('Direction',0)

            loc.encode = LocationEncodeType.BD.value
            loc.address = data.get('PlaceName','') + data.get('RoadName','')
            loc.text = data.get('Status','')
            loc.status = 0

            loc.extra['Odometer'] = data.get('Odometer',0)   #	里程
            loc.extra['address'] = data.get('PlaceName','')
            loc.extra['status'] = data.get('Status','')     #ACC开,3D定位,天线正常,冷机开,门关,门关4
            loc.extra['Provice'] = data.get('Provice','')   # 省
            loc.extra['City'] = data.get('City','')   # 市
            loc.extra['District'] = data.get('District','')   # 区
            loc.extra['RoadName'] = data.get('RoadName','')   # 路名信息
            loc.extra['T1'] = data.get('T1','')   # 温度1(℃)
            loc.extra['T2'] = data.get('T2','')   # 温度2(℃)
            loc.extra['T3'] = data.get('T3','')   # 温度3(℃)
            loc.extra['T4'] = data.get('T4','')   # 温度4(℃)
            loc.extra['Lat02'] = data.get('Lat02','')   # 根据参数isoffsetlonlat返回的纬度
            loc.extra['Lon02'] = data.get('Lon02','')   # 根据参数isoffsetlonlat返回的纬度
            loc.extra['AreaName'] = data.get('AreaName','')   # 地标名称
            loc.extra['Time1'] = data.get('Time1','')   # 温度1采集时间 2014-10-16 08:48:54
            loc.extra['Time2'] = data.get('Time2','')   # 温度1采集时间 2014-10-16 08:48:54
            loc.extra['Time3'] = data.get('Time3','')   # 温度1采集时间 2014-10-16 08:48:54
            loc.extra['Time4'] = data.get('Time4','')   # 温度1采集时间 2014-10-16 08:48:54
            self._onDataReady( vehicle_id,loc )
