#coding:utf-8

from flask import Blueprint,request,g
from camel.biz.application.flasksrv import instance,db


"""
1. 获取指定车辆名称的位置信息(支持多车辆)
2. 查询指定车辆名称的历史位置信息
3.

"""
# @app.route('/car')
def get_vehicles():
    """查询车辆"""

    instance.getLogger().debug('abccc')
    instance.getLogger().addTag('TRANS:A001')
    # print request.values
    do_request()
    return 'i am car!'

def do_request():
    instance.getLogger().debug('xxx')


# @app.route('/cat')
def cat():
    import time
    time.sleep(.2)
    instance.getLogger().debug('miao~')
    return 'i am cat!'


# @app.route('/online')
def lines():

    line = Online()
    line.get_time = '2017-1-1'
    line.mobile = '13916624477'

    db.session.add(line)
    db.session.commit()

    return 'one online record  be created! <%s>'%line.id