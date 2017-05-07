#!/bin/bash

export LC_ALL=en_US.UTF-8
pwd=$(cd `dirname $0`;pwd)

CAMEL_LIB=/Users/scott/Desktop/yto/svn/dev_package/python

##APP_NAME##

if [ -z $CAMEL_HOME ]; then
	export CAMEL_HOME=$pwd/../
fi

if [ $APP_NAME ]; then
	APP_PATH=$CAMEL_HOME/products/$APP_NAME
else
	APP_PATH=$pwd/../src
fi

export PYTHONPATH=$CAMEL_LIB:$APP_PATH

echo $CAMEL_HOME

uwsgi --socket 127.0.0.1:5555 --chdir $APP_PATH --module wsgi --callable app --stats 127.0.0.1:9191

#-p 8 --workers 4 --buffer-size 131072
#--socket-timeout 10
#--threads 40 --workers 2

#--chdir
#--wsgi-file
#

######################
## Nginx settings ##
#
# location / {
#	    include uwsgi_params;
#	    uwsgi_pass 127.0.0.1:5555;
#	}
#
