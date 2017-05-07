

#rhinoceros系统 － 数据规格定义


Revisions: 	
	

	2016.5.1  zhangbin 	created
	version: 0.1
	

##目录





## 1. 常数定义



###1.1 位置数据供应商码 ProviderType


|名称|编码|类型|说明|
|-|-|-|-|
|G7|1|int|G7|
|ZJXL|2|int|中交兴路|
|YL|3|int|易流|
|ZQ|4|int|重汽|
|KMS|5|int|康明斯|

###1.2 接收设备类型 LocationDeviceType


|名称|编码|类型|说明|
|-|-|-|-|
|GPS|1|int|GPS定位数据|
|BD|2|int|北斗定位数据|


###1.3 坐标类型 LocationEncodeType


|名称|编码|类型|说明|
|-|-|-|-|
|WGS84|1|int|GPS|
|GCJ|2|int|国测局|
|BD|3|int|百度坐标BD9|

###1.4 采集数据类型 DataCategoryType
|名称|编码|类型|说明|
|-|-|-|-|
|LOC|A|string|位置信息|
|EMS|B|string|发送机数据|
|ETC|C|string|ETC数据|

###1.5 定位数据规格LocationData
|名称|二级|类型|说明|
|-|-|-|-|
|type||string|数据类型(LOC,EMS,ETC)）|
|version||string|版本|
|provider||int|数据供应商码(G7,ZJXL,ZQ,YL,KMS)|
|moid||string|设备标识码|
|lon||float|经度|
|lat||float|纬度|
|speed||float|速度|
|direction||float|方向|
|time||int|gps定位时间|
|altitute||float|高度|
|encode||int|坐标类型 {WGS84,GCJ,BD}|
|status|0|int|状态 RUNNING:1,STOPPED:2,OFFLINE:3|
|address||string|地址，例如： 金钟路231号|
|text||string|文本描述，例如：ACC/ON...|
|extra||dict|额外未定义属性|




  	
## 2. 数据封包
###2.1 DataEnvelope 

不同的采集数据在被传送到外部系统时需要将其进行封包（数据列集）。adapter接入的位置数据、etc等数据被组装到DataEnvelope中统一封包传送。数据编码方式: json (utf-8)

|名称|编码|类型|说明|
|-|-|-|-|
|id||string|车辆识别号(车牌)|
|provider||int|数据提供商 ProviderType|
|payloads||dict|数据集合(DataCategory) {数据类型:数据内容})|

####Examples

	{
	  	id: '沪A20982',
	  	provider: 1,
	  	payloads: {
	  		'A':{           #位置数据
	  			type: 1,
	  			version: '0.1',
	  			provider: 1 ,
	  			moid: '沪A20982',
	  			lon: 121.22,
	  			lat: 31.11
	  			speed: 90,
	  			direction: 123,
	  			time: 14000999232,
	  			altitue: 12,
	  			encode: 2 ,
	  			status: 1,
	  			address: '',
	  			text: ''
	  			
	  		},
	  	}
	 } 
	 
	

