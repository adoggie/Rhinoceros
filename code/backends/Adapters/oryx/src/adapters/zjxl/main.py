#coding:utf-8

import os.path
import hashlib
import json
import requests
import urllib
import gevent

from camel.fundamental.utils.timeutils import str_to_timestamp
from camel.fundamental.application.app import Application,instance
from ..adapter import AdapterBase
from camel.rhinoceros.base import LocationData,ProviderType,LocationEncodeType
from camel.rhinoceros.coord_transform import wgs84_to_bd09
import crypto

class AdapterZXJY(AdapterBase):
    def __init__(self,cfgs):
        AdapterBase.__init__(self,cfgs)
        self.token = None

    def open(self):
        self._init()
        # AdapterBase.open(self)
        # self._auth()
        self.task = gevent.spawn(self._task_exec)
        # self._request_getLocation([u'陕YH0009'])  # ZJXL
        return True

    def _makeRequestParams_getLocation(self,plate):

        carnums = plate
        time = self.format_ymdhms()
        transaddr =  3

        query_params = {'carnums': carnums, 'isbind': 1,
            'transaddr': transaddr}

        sign = self._makeSign( query_params )
        data = query_params
        payload = {
            'method':'truck.device.getTruckAddress',
            'timestamp':self.format_ymdhms(),
            'app_key': self.cfgs.get('account'),
            'sign':sign,
            'data':data
        }

        return json.dumps(payload)

    def _makeSign(self,params):

        keys = params.keys()
        keys = sorted(keys)
        stream = ''
        for key in keys:
            value = params[key]
            stream+=key+str(value)
        screct_key = self.cfgs.get('password')
        stream = screct_key+stream+screct_key
        md = hashlib.md5()
        md.update(stream)
        digest = md.hexdigest().upper()
        return digest


    def _auth(self):

        params = {'user': self.cfgs.get('account'), 'pwd': self.cfgs.get('password')}

        data = urllib.urlencode(params)
        data = crypto.encode(data)
        params={
            'client_id': self.cfgs.get('client_id')
        }

        url = self.cfgs.get('auth_url') + '/' + data
        # print 'auth request:'+ url
        cert = os.path.join(instance.getConfigPath(),self.cfgs.get('cert_file'))
        resp = requests.post(url,params,verify=cert)
        # print resp.text
        data = crypto.decode(resp.text)
        data = json.loads(data)
        if data.get('status') !=1001:
            instance.getLogger().warning('adapter(zjxl) auth request failed. status:%s'%data.get('status'))
            return False
        self.token = data.get('result')
        instance.getLogger().debug('adapter(zjxl) auth-token:'+ self.token)

    #多车
    def __request_getLocation(self,vehicles):

        self._auth()
        # for vehicle_id in vehicles:
        carnums = ','.join(vehicles)

        params = {'token': self.token, 'vclN': carnums.encode('utf-8'),'timeNearby':30 }
        data = urllib.urlencode(params)
        data = crypto.encode(data)

        url = self.cfgs.get('access_url_batch') +'/' + data
        params = {'client_id': self.cfgs.get('client_id')}

        cert = os.path.join(instance.getConfigPath(), self.cfgs.get('cert_file'))
        resp = requests.post(url, params, verify=cert)
        print resp.text
        data = crypto.decode(resp.text)
        data = json.loads(data)
        if data.get('status') != 1001:
            instance.getLogger().warning('adapter(zjxl) getLocation request failed. status:%s'%data.get('status'))
            return False

        resp = requests.post(url, data=params)
        content = resp.json()
        if content.get('code', -1) != 0:  # 0: okay else false
            return
        data = content.get('result', {})
        loc = LocationData(vehicle_id)  # spawn location point
        loc.version = '0.1'
        loc.provider = ProviderType.ZJXL.value
        loc.lon = int(data.get('lng', 0))/600000.0
        loc.lat = int(data.get('lat', 0))/600000.0
        loc.speed = float(data.get('spd', 0))
        loc.time = int(data.get('utc', 0))  #
        loc.direction = int( data.get('drc',0))
        loc.extra['address'] = data.get('adr', '')
        self._onDataReady(vehicle_id, loc)


    #单车
    def _request_getLocation(self,vehicles):
        # return self.__request_getLocation(vehicles)

        self._auth()
        for vehicle_id in vehicles:
        # carnums = ','.join(vehicles)

            params = {'token': self.token, 'vclN': vehicle_id.encode('utf-8'),'timeNearby':30 }
            data = urllib.urlencode(params)
            data = crypto.encode(data)

            url = self.cfgs.get('access_url') +'/' + data
            params = {'client_id': self.cfgs.get('client_id')}

            cert = os.path.join(instance.getConfigPath(), self.cfgs.get('cert_file'))
            resp = requests.post(url, params, verify=cert)
            # print resp.text
            data = crypto.decode(resp.text)
            data = json.loads(data)
            if data.get('status') != 1001:
                instance.getLogger().warning('adapter(zjxl) getLocation request failed. status:%s'%data.get('status'))
                return False
            loc = self.assignLocation(vehicle_id,data)
            self._onDataReady(vehicle_id, loc)

    def assignLocation(self,vehicle_id,data):
        loc = LocationData(vehicle_id)  # spawn location point
        loc.version = '0.1'
        loc.provider = ProviderType.ZJXL.value
        loc.lon = int(data.get('lng', 0)) / 600000.0
        loc.lat = int(data.get('lat', 0)) / 600000.0
        loc.lon,loc.lat = wgs84_to_bd09(loc.lon,loc.lat)
        loc.encode = LocationEncodeType.BD.value
        loc.speed = float(data.get('spd', 0))
        loc.time = int(data.get('utc', 0))  #
        loc.direction = int(data.get('drc', 0))
        loc.address = data.get('adr', '')
        loc.status = 0
        loc.text = ''

        loc.extra['address'] = data.get('adr', '')
        loc.extra['bst'] = data.get('bst','')
        loc.extra['alc'] = data.get('alc')

        return loc
