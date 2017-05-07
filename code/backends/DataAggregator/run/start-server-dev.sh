#!/bin/bash

# you must ensure CAMEL_LIB is correctly set.

export LC_ALL=en_US.UTF-8
pwd=$(cd `dirname $0`;pwd)

if [ -z $CAMEL_LIB ]; then
	export CAMEL_LIB=/Users/scott/Desktop/yto/svn/dev_package/python
fi

if [ -z $CAMEL_HOME ]; then
	export CAMEL_HOME=$pwd/../
fi

##APP_NAME##

if [ $APP_NAME ]; then
	APP_PATH=$CAMEL_HOME/products/$APP_NAME
else
	APP_PATH=$pwd/../src
fi

export PYTHONPATH=$CAMEL_LIB:$APP_PATH

#echo $CAMEL_HOME

python $APP_PATH/server.py

