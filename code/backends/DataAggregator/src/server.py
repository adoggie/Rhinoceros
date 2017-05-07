#coding:utf-8

import sys
import getopt

from camel.biz.application.corsrv import CoroutineApplication,setup,instance
from camel.fundamental.amqp import AmqpManager,AccessMode
from service.accumulate import Accumulator

class Aggregator(CoroutineApplication):
    def __init__(self):
        CoroutineApplication.__init__(self)

    def init(self):
        CoroutineApplication.init(self)
        AmqpManager.instance().init(self.getConfig().get('amqp_config'))
        Accumulator.instance().init(self.getConfig().get('aggregator'))

    def run(self):
        AmqpManager.instance().getMessageQueue('mq_2').open(AccessMode.READ)
        CoroutineApplication.run(self)

    def _terminate(self):
        AmqpManager.instance().terminate()
        CoroutineApplication._terminate(self)

setup(Aggregator).run()


