#coding:utf-8

from camel.fundamental.application.app import instance
from camel.fundamental.utils.useful import Singleton
from camel.fundamental.utils.importutils import import_class,import_function


class AdapterManager(Singleton):
    def __init__(self):
        self.cfgs = None
        self.adpaters ={}


    def init(self,cfgs):
        self.cfgs = cfgs
        for cfg in self.cfgs:
            if not cfg.get('enable',False):
                continue
            cls = import_function( cfg.get('module') )
            adapter = cls(cfg)
            res = adapter.open()
            if res:
                self.registerAdapter(adapter.name,adapter)
            else:
                instance.getLogger().error('adapter %s open failed!'%adapter.name)


    def registerAdapter(self,name,adapter):
        self.adpaters[name] = adapter
        instance.getLogger().info('adapter: %s has been loaded..'%name)




