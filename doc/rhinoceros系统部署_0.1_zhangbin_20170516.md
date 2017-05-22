#rhinoceros系统部署

	v0.1  zhangbin  2017-5-16  new
	

##1.系统组成 

###1.1系统服务：

	adapter  		接入服务
	shuffler 		数据清洗
	aggregator 		数据聚合处理服务
	tracer    		车辆实时位置跟踪服务
	locuserserver 	位置用户服务

###1.2 中间件服务：
	
	postgresql-server 9.4.1+  	数据库
	redis-server 2.7+ 			缓存数据库
	qpid-1.3.5					消息队列

##2.运行环境 






###2.1服务器资源

	server-1  数据库和中间件服务*
	hostname: rhino-db
	ip: 118.190.114.48 / 10.31.49.22
	+postgresql-server  9.4.1
	+redis-server
	+qpid-server 1.3.5
    xpublic-port: 15672, 16379, 15432*

	server-2  应用服务器
	hostname: rhino-server1
	ip: 118.190.1.71 / 10.26.176.193
    +teresa 服务( tomcat 7 ) 
    +nginx
    public-port: 8088
   
	server-3  应用服务器
    hostname: rhino-server2
    ip: 118.190.113.106/10.31.49.207   
    +datashuffler
    +aggregator 
    +tracer 
    +locuserservice
    +nginx 
    public-port: 8088

数据库采用pgsql的nosql存储方式，数据库独立部署在一台虚机，配置500G磁盘，存放车辆历史轨迹。 


##3.中间件配置
###3.1 postgresql

	
	安装 postgresql 9.4.1+ 
	
	修改 pg_hba.conf , postgresql.conf  开放对外访问权限
	
	初始化数据目录
		mkdir /data
		su - postgres -c " pg_ctl initdb -D /data/pgsql"
		
	启动数据库实例
		su - postgres -c "pg_ctl -D /data/pgsql -l logfile start"
		
	修改数据库用户密码
		su - postgres -c "psql -c \"alter user postgres with password 'xxxx' \" " 
		
	创建数据库
		su - postgres -c "createdb rhino"	
	
	
###3.2 qpid 
	
	yum install qpid 
	
	修改配置:  /etc/qpidd.conf 
		
		auth=no
		
	service qpidd start 
	
###3.3 redis-server
	yum install redis 
	service redis start 
	
	修改配置： /etc/redis.conf
	访问密码:  requirepass 13916624477
	访问地址:  bind 127.0.0.1 118.190.89.205 

###3.4 pip 安装包 
 
 	kafka-python
	flask
	celery
	pykafka
	flask-login
	flask-openid
	flask-mail
	flask-sqlalchemy
	sqlalchemy-migrate
	flask-whooshalchemy
	flask-wtf
	flask-babel
	virtual-env
	gevent
	psycopg2
	uwsgi
	flask-cors
	pyDes
	jpype1
	requests
	psycogreen
	gevent-psycopg2
	redis
	xpinyin
	PyYAML
	python-dateutil
	
###3.5 Nginx 配置 
	启用gzip 
	
	gzip on;
    gzip_min_length 1k;
    gzip_buffers 16 64k;
    gzip_vary on;
    gzip_types text/plain application/json
    
	location /rhino/{
                        proxy_redirect off;
                        proxy_set_header Host $host;
                        proxy_set_header X-Real-IP $remote_addr;
                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                        proxy_pass http://127.0.0.1:15003/rhino/;
        }

	location /rhino/auth/{
                        proxy_redirect off;
                        proxy_set_header Host $host;
                        proxy_set_header X-Real-IP $remote_addr;
                        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                        proxy_pass http://127.0.0.1:15001/rhino/auth/;
        }
        
##4. Docker配置	

docker image:   **rhino_0.2.docker**

###4.1 server-1
	
	- 创建container -
	bash /opt/docker/docker_db_start.sh 
	bash /opt/docker/docker_redis_qpid_start.sh 
	
	- 配置container -
	docker exec -it rhino-db rhino_0.2 /bin/bash
	
	- postgresql -
	bash /opt/scripts/init_pgsql.sh
	bash /opt/scripts/start_pgsql.sh
	bash /opt/scripts/stop_pgsql.sh
	- qpid - 
	bash /opt/scripts/start_qpid.sh 
	bash /opt/scripts/stop_qpid.sh
	- redis - 
	bash /opt/scripts/start_redis.sh 
	bash /opt/scripts/stop_redis.sh
	
	
###4.2 server-2
	- 创建container -
	bash /opt/docker/docker_service_start.sh
	
	- 启动服务 - 
	bash /opt/services/start-adapter.sh  [front]
	bash /opt/services/start-tracer.sh [front]
	- 停止服务 - 
	bash /opt/services/DataTracer/run/stop-server-dev.sh
	
	

##5.服务配置

rhino服务后台子系统的目录结构：
	
	DataTracer/
		├── data
		├── etc
		├── logs
		├── run
		├── scripts
		├── src
		└── tests
	
	etc/settings.yaml  服务配置程序
	run/start-server-dev.sh 服务运行脚本
	
	
###4.1 Adapter

	amqp_config
		- name: 'mq_mess'
	      host: 'ytodev2'		#修改对应server-3的ip地址
    	  port: 5672			# qpid的端口号
    	 
###4.2 Aggregator
	
	amqp_config
		- name: 'mq_2'
	      host: 'ytodev2'		#修改对应server-3的ip地址
    	  port: 5672			# qpid的端口号
    
	aggregator:
		data_span: 5 # 5分钟累积
		distance: 2 # 两个时间累积段之前的数据开始写入持久层
		data_path: 'cache'
		backup_path: 'back'
		persistence:
    		handlers:
      		  - name: 'pgsql'
        		host: 'ytodev2'		#数据库主机ip
        		port: '5432'		#数据库端口	
        		dbname: 'rhino'		#数据库名称
        		user: 'postgres'	#用户名
        		password: '13916624477'	#密码
    		
	
###4.3 Shufffler

	amqp_config
		- name: 'mq_1'
	      host: 'ytodev2'		#修改对应server-3的ip地址
	    - name: 'mq_2'
	      host: 'ytodev2'		#修改对应server-3的ip地址
	    - name: 'mq_3'
	      host: 'ytodev2'		#修改对应server-3的ip地址

###4.4 Tracer
	
	http:
	  host : '127.0.0.1'  # http 侦听地址
	  port : 15003		   # 侦听端口

	cache_config:
		default:
    		type: redis
    		host: 'ytodev2'
	    	port: 6379
    		password: '13916624477'
    		enable: true    	
    		
    amqp_config:
	  - name: 'mq_mess'
    	type: 'qpid'
	    host: 'ytodev2'
    	port: 5672
    	
    data_tracer:
    	database:
	    	host: 'ytodev2'
    		port: 5432
    		user: 'postgres'
    		password: '13916624477'
    		dbname: 'rhino'

###4.5 LocUserService
	
	cache_config:
	  default:
    	type: redis
	    host: 'ytodev2'
    	port: 6379
	    password: '13916624477'
    http:
    	host : '127.0.0.1'
		port : 15001

##5. 公共组件配置
###5.1 camel lib 

camel-lib 是python应用程序组件包，系统服务均依赖此功能包。

	export CAMEL_LIB=$camel_path
