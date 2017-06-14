#!/usr/local/bin/jython
#coding:utf-8

import quickfix.FieldNotFound
import quickfix.fix44.Message

class AccountInfoRequest(quickfix.fix44.Message): 
    def __init__(self):
        self.serialVersionUID = -3033519792313574631L;
        self.MSGTYPE = "U1000";
        Message.__init__() 
        self.getHeader().setField(new quickfix.field.MsgType(MSGTYPE))

    def set(self,value):
        self.setField(value)

    def get(self,value):
        self.getField(value)
        return value

    def getAccReqID(self):
        value = AccReqID()
        self.getField(value)
        return value
    def get(self,value):
        self.getField(value)
        return value
    def getAccount(self):
        value = quickfix.field.Account()
        self.getField(value)
        return value
    def set(self,value):
        self.setField(value)