#coding:utf-8

import os.path

from jpype import *

jvmpath = getDefaultJVMPath()

path = os.path.dirname(os.path.abspath(__file__))
jarpath = os.path.join(path,'java/zjxl.jar')
startJVM(jvmpath, "-ea", "-Djava.class.path="+jarpath)

def encode( data ):
    # cls = JPackage('zjxl').SignZJXL
    cls = JClass('SignZJXL')
    # codec = cls()
    result = cls.encode(data)
    return result

def decode( data ):
    cls = JPackage('zjxl').SignZJXL
    # codec = cls()
    cls = JClass('SignZJXL')
    result = cls.decode(data)
    return result

# shutdownJVM();


if __name__=='__main__':
    text = encode("shanghai")
    print text
    print decode(text)