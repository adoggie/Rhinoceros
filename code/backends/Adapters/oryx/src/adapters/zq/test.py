#coding:utf-8

from zeep import Client

"""
返回结果:json 格式字符串。依次为:
gpssj GPS 时间;
zs 发动机转速;
cs 车 速;
sw 水温;
ssyh 瞬时油耗;
nj 扭矩;
zlc 总里程;
zyh 总油耗;
ssyl 剩余油 量;
ym 油门;
dw 档位;
fdjsj 发动机工作时间;
hb 海拔;
jd 经度;
wd 纬度;
"""

import json

wsdl_auth = 'http://www.sinotruksfs.com/tele_gps/WebService.asmx?wsdl'
wsdl_auth = 'http://www.sinotruksfs.com/tele_gps/ytkd.asmx?wsdl'
userid=u'圆通速递'
vehicle = 'GC209059,GC209656'
vehicle = 'GC209059'

client = Client( wsdl= wsdl_auth)
result = client.service.get_running_info(userid,vehicle)
print json.loads(result)
