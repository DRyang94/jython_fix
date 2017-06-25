#!/usr/local/bin/jython
#coding:utf-8
# package com.btcchina.fix.util;
import sys
import os

from xml.etree import ElementTree

testlogpth = '../data/btcc_client_log/FIX.4.4-02f8e7cb-6a9a-4dff-8ab8-e246b8d18002-BTCC-FIX-SERVER.messages.log'

class MsgJythonPrint():
    def __init__(self,fixxmlpth = 'data/selfFIX44.xml'):
        self.fixpth = fixxmlpth
        f = open(self.fixpth,'r')
        text = f.read()
        f.close()
        self.fix44Root = ElementTree.parse(self.fixpth) 
        self.fieldDic = {}
        self.fieldDataTypeDic = {}
        self.fieldDataValueEnum = {}

        self.initFieldDic()

    def initFieldDic(self):
        node_find = self.fix44Root.find('fields')  
        node_findalls = node_find.findall("field")
        for n in node_findalls:
            self.fieldDic[str(n.attrib['number'])] = n.attrib['name']
            self.fieldDataTypeDic[n.attrib['name']] = n.attrib['type']
            self.setFieldValue(n)

    def setFieldValue(self,fieldnode):
        valuenodes = fieldnode.findall('value')
        if valuenodes:
            valuetmp = {}
            for v in valuenodes:
                valuetmp[v.attrib['enum']] = v.attrib['description']
            self.fieldDataValueEnum[fieldnode.attrib['number']] = valuetmp

    #打印输出收到的消息
    def mpprint(self,msg):
        outstr = ''
        dats = msg.split('\x01')
        for d in dats:
            kv = d.split('=')
            if len(kv) == 2:
                outstr += self.getFieldName(kv[0]) + ':' + str(kv[1]) + '\n'
        print '-----------------------------'
        print outstr

    #读取tag枚举型数据描述字典
    def getDieldValueDicWithTag(self,tag):
        if self.fieldDataValueEnum.has_key(str(tag)):
            return self.fieldDataValueEnum[str(tag)]
        return None
    #读取Field名称枚举型数据描述字典
    def getDieldValueDicWithName(self,fname):
        tagtmp = self.getFieldTagWithName(fname)
        if tagtmp and self.fieldDataValueEnum.has_key(str(tagtmp)):
            return self.fieldDataValueEnum[str(tagtmp)]
        return None  
    #读取消息tag名称
    def getFieldName(self,tag):
        strtag = str(tag)
        if strtag in self.fieldDic.keys():
            return self.fieldDic[strtag]
        else:
            return None
    #读取消息tag数据类型
    def getFieldDataType(self,tag):
        strtag = str(tag)
        if strtag in self.fieldDic.keys():
            fname = self.fieldDic[strtag]
            return self.fieldDataTypeDic[fname]
        else:
            return None

    #获取tag名称
    def getFieldTagWithName(self,name):
        for k in self.fieldDic.keys():
            if self.fieldDic[k] == name:
                return k
        return None

    #解析fix消息为tag字典
    def getMsgDicFromMsgForTag(self,msg):
        dictmp = {}
        dats = msg.split('\x01')
        for d in dats:
            kv = d.split('=')
            if len(kv) == 2:
                dictmp[str(kv[0])] = str(kv[1])
        return dictmp
    #解析fix消息为名称和值字典
    def getMsgDicFormMsgForName(self,msg):
        dictmp = {}
        dats = msg.split('\x01')
        for d in dats:
            kv = d.split('=')
            if len(kv) == 2:
                nametmp = self.getFieldName(kv[0])
                dictmp[nametmp] = str(kv[1])
        return dictmp

    #获取消息中字段值
    def getFieldValueWithName(self,msg,fname):
        msgdic = self.getMsgDicFormMsgForName(msg)
        if msgdic.has_key(fname):
            return msgdic[fname]
        else:
            return None
    #获取消息中tag对应值
    def getFieldValueWithTag(self,msg,tag):
        msgdic = self.getMsgDicFromMsgForTag(msg)
        if msgdic.has_key(str(tag)):
            return msgdic[str(tag)]
        else:
            return None

if __name__ == '__main__':
    msgtool = MsgJythonPrint()
    f = open(testlogpth,'r')
    loglines = f.readlines()
    f.close()
    outs = []
    for l in loglines:
        tmpl = l.replace('\n','')
        outs.append(tmpl)
    print outs
    print msgtool.getFieldValueWithTag(outs[0], 35)
    print msgtool.getFieldValueWithName(outs[0], 'MsgType')
    print msgtool.getFieldName(8)

