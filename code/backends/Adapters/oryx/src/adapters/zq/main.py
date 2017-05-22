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
import string
from zeep import Client

from camel.fundamental.application.app import instance
from camel.fundamental.utils.timeutils import str_to_timestamp
from ..adapter import AdapterBase
from camel.rhinoceros.base import LocationData,ProviderType

"""

"""

class AdapterZQ(AdapterBase):
    def __init__(self,cfgs):
        AdapterBase.__init__(self,cfgs)

    # def open(self):
    #     self._init()
    #
    #     # self.task = gevent.spawn(self._task_exec)
    #     self.doBatchRequest(self.vehicles[:1])
    #     return True

    def _repeated(self):
        return True

    def _request_getLocation(self,vehicles):
        """微线程执行 车辆位置信息的请求获取

        :param vehicle_id:  车辆标识码 或者 车牌
        :return:

        """
        wsdl = self.cfgs.get('access_url')
        username = self.cfgs.get('account')

        sn_list = []
        for _ in vehicles:
            plate, sn = map(string.strip, _.split('\t'))
            sn_list.append(sn)

        carnums = ','.join(sn_list)


        result=[]
        try:
            client = Client(wsdl=wsdl)
            result = client.service.get_running_info(username, carnums)
            result = json.loads(result)
            self.dbg_req_num += len(sn_list)
        except:
            instance.getLogger().warning('getLocation error.  vehicle:%s '%(carnums))

        for data in result:
            if data.get('gpsbz','') == '56':
                continue  # 数据无效
            vehicle_id = data.get('cph','').strip()
            loc = LocationData( vehicle_id)  # spawn location point
            loc.version = '0.1'
            loc.provider = ProviderType.ZQ.value
            loc.lon = data.get('jd',0)
            loc.lat = data.get('wd',0)
            loc.speed = data.get('cs',0)
            loc.altitute = data.get('hb',0)
            loc.time = str_to_timestamp( data.get('gpssj',0) ) # todo. format timestamp
            loc.text =u'设备号:%s,水温:%s,总里程:%s,总油耗:%s '%(data.get('sbh',''),
                data.get('sw',0),data.get('zlc',0),data.get('zyh',0)
            )
            loc.status = 0
            loc.address = data.get('addr','')
            loc.direction = data.get('fx',0)

            loc.extra['lisno'] = data.get('lisno','')   #	机构号
            loc.extra['cjh'] = data.get('cjh','') # 车辆类型 1为自建车辆，3为外部共享车辆
            loc.extra['sbh'] = data.get('sbh','')  # 设备号
            loc.extra['lx'] = data.get('lx','')
            loc.extra['zs'] = data.get('zs',0)        # 离线持续时间(s)
            loc.extra['sw'] = data.get('sw',0)        # 水温
            loc.extra['ssyh'] = data.get('ssyh',0)    # 瞬 时油耗
            loc.extra['nj'] = data.get('nj',0)    # 瞬 时油耗
            loc.extra['zlc'] = data.get('zlc',0)    # 总里程
            loc.extra['zyh'] = data.get('zyh',0)    # 总油耗
            loc.extra['ssyl'] = data.get('ssyl',0)    # 剩余油量
            loc.extra['ym'] = data.get('ym',0)    # 油 门
            loc.extra['dw'] = data.get('dw',0)    # 档位
            loc.extra['fdjsj'] = data.get('fdjsj',0)    # 发动机工作时间

            print loc.dict()
            print 'batch request num:', self.dbg_req_num
            self.dbg_resp_num += 1
            print  'recieved locations num:', self.dbg_resp_num
            self._onDataReady( vehicle_id,loc )


"""
lisno 序号,cjh 车架号,cph 车牌号 sbh 设备号,lx 数据情 况,gpssj GPS 时间;
zs 发动机转速;cs 车速;sw 水温;ssyh 瞬 时油耗;nj 扭矩;zlc 总里程;
zyh 总油耗;ssyl 剩余油量;ym 油 门;dw 档位;fdjsj 发动机工作时间;hb 海拔;
jd 经度;wd 纬 度;

SQL 查询
--------
select  distinct(id) from  mo_data_20170519 where (last::json#>>'{data,A,provider}') = '4' ;

"""