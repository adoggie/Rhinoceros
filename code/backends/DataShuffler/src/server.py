#coding:utf-8

import sys
import getopt

from camel.biz.application.corsrv import CoroutineApplication,setup,instance
from camel.fundamental.amqp import AmqpManager,AccessMode

class AdapterServer(CoroutineApplication):
    def __init__(self):
        CoroutineApplication.__init__(self)

    def init(self):
        CoroutineApplication.init(self)
        AmqpManager.instance().init(self.getConfig().get('amqp_config'))

    def run(self):

        AmqpManager.instance().getMessageQueue('mq_2').open(AccessMode.WRITE)
        AmqpManager.instance().getMessageQueue('mq_3').open(AccessMode.WRITE)
        AmqpManager.instance().getMessageQueue('mq_1').open(AccessMode.READ)
        CoroutineApplication.run(self)

    def _terminate(self):
        AmqpManager.instance().terminate()
        CoroutineApplication._terminate(self)

setup(AdapterServer).run()


