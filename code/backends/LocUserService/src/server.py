#coding:utf-8

import sys
import getopt

# from camel.biz.application.corsrv import CoroutineApplication,setup,instance
from camel.biz.application.corflasksrv import CoroutineFlaskApplication,setup,instance

from camel.fundamental.amqp import AmqpManager,AccessMode
from service.users import UserManager


class AdapterServer(CoroutineFlaskApplication):
    def __init__(self):
        CoroutineFlaskApplication.__init__(self)

    def init(self):
        CoroutineFlaskApplication.init(self)
        # AmqpManager.instance().init(self.getConfig().get('amqp_config'))
        cfgs = self.getConfig()
        UserManager.instance().init(cfgs.get('user_service'))


    def run(self):
        # AmqpManager.instance().getMessageQueue('mq_mess').open(AccessMode.READ)
        CoroutineFlaskApplication.run(self)

    def _terminate(self):
        AmqpManager.instance().terminate()
        CoroutineFlaskApplication._terminate(self)

setup(AdapterServer).run()


