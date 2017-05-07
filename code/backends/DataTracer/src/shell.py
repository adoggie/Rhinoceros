#coding:utf-8


from camel.biz.application.flasksrv import setup,db
setup()

from  model.user import User
from camel.model.log.models import *
from camel.model.camel import *


db.create_all()






