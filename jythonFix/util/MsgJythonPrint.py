#!/usr/local/bin/jython
#coding:utf-8
# package com.btcchina.fix.util;
import sys
import os

testlogpth = '../data/btcc_client_log/FIX.4.4-02f8e7cb-6a9a-4dff-8ab8-e246b8d18002-BTCC-FIX-SERVER.messages.log'

class MsgJythonPrint():
    def __init__(self):
        pass

    def mpprint(self,msg):
        print msg
        dats = msg.split('\x01')
        print dats


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
    msgtool.mpprint(outs[0])
