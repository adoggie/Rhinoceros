#coding:utf-8

from flask import request,g
from camel.biz.application.flasksrv import instance,db

from service.users import UserManager

def getTickets():
    """"""
    print request.values.get('name')
    app_id = request.values.get('app_id')
    secret_key = request.values.get('secret_key')
    user_id = request.values.get('user_id')
    result = UserManager.instance().authenticate(app_id,secret_key,user_id)
    return  result.json

