#!/usr/local/bin/jython
#coding:utf-8
# package com.btcchina.fix;

import quickfix.StringField

class AccReqID(quickfix.StringField):
    def __init__(self,data = ''):
        self.serialVersionUID = 2330170161864948797L;
        self.FIELD = 8000
        if data == '':
            quickfix.StringField.__init__(self,8000)
        else:
            quickfix.StringField.__init__(self,FIELD,data)
