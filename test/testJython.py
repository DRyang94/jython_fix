#!/usr/local/bin/jython
#coding:utf-8
#导入Java标准类库
#如果是jar包，需要sys.path.append(jar_file)
from java.util import Random  

#导入自定义类库
import Foo

foo = Foo()
print foo.getName()
foo.setName("change")
print foo.getName()

#调用Java标准类库
random = Random()
print random.nextInt(100)