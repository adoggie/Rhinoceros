#coding:utf-8

from camel.fundamental.utils.useful import Singleton
from camel.rhinoceros.base import DataEnvelope,DataCategory
from camel.fundamental.amqp import AmqpManager,AccessMode


class ShuffleService(Singleton):
    def __init__(self):
        self.cfgs = {}

    def init(self,cfgs):
        self.cfgs = cfgs
        return self

    def onDataRecieved(self,data):
        mq2 = AmqpManager.instance().getMessageQueue('mq_2')
        mq3 = AmqpManager.instance().getMessageQueue('mq_3')
        mq2.produce(data)
        mq3.produce(data)
