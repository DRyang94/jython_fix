#!/usr/local/bin/jython
#coding:utf-8
# package com.btcchina.fix.util;
import sys

import java.util.Iterator as Iterator
import java.util.LinkedList as LinkedList
import java.lang.Math as Math

import org.apache.log4j.Logger as Logger

import BTCCMarketDataRequest
import BTCCTradingRequest
import MessagePrinter

import quickfix.ConfigError as ConfigError
# //import javax.xml.parsers.DocumentBuilderFactory;
# //import javax.xml.parsers.DocumentBuilder;
# //
# //import org.w3c.dom.Document;
# //import org.w3c.dom.NodeList;
# //import org.w3c.dom.Node;
# //import org.w3c.dom.Element;
import quickfix.DataDictionary as DataDictionary
import quickfix.Field as Field
import quickfix.FieldMap as FieldMap
import quickfix.FieldNotFound as FieldNotFound
import quickfix.FieldType as FieldType
import quickfix.Group as Group
import quickfix.Session as Session
import quickfix.SessionID as SessionID
import quickfix.field.MsgType as MsgType
import quickfix.fix44.Message as Message


import threading
import math
import time
import MsgJythonPrint

class AccountManger():
    def __init__(self,pID,pStepPrice,pTradeCount,plog):
        self.log = plog #Logger.getLogger(AccountManger)      #//log输出工具
        self.dataDict = DataDictionary("data/selfFIX44.xml")                            #//new DataDictionary("FIX44.xml"); //fix4.4协议
        self.msgPrinter = MessagePrinter.MessagePrinter()
        self.jythonPrinter = MsgJythonPrint.MsgJythonPrint()
        self.sessionID = pID                           #//fix绘话ID

        #最新成交价
        self.tradePrice = 0.0                           #最新成交价
        self.buyPrice = 0.0                             #最新买一价 
        self.sellPrice = 0.0                            #是新卖一价

    def decodePriceData(self,msg):
        tmpmsg = msg.split(chr(0x01))
        print len(tmpmsg)
        outdats =  {}
        datacount = 0
        datas = []
        tmps = []
        for d in tmpmsg:
            tmpdat = d.split('=')
            if len(tmpdat) > 1:
                tagtmp = tmpdat[0]
                valuetmp = tmpdat[1]
                if tagtmp == '268':
                    datacount = int(valuetmp)
                if tagtmp == '269':
                    tmps.append(valuetmp)
                if tagtmp == '270':
                    tmps.append(float(valuetmp))
                    datas.append(tmps)
                    tmps = []
        for v in datas:
            if v[0] == '0':#买一价
                self.buyPrice = v[1]
            if v[0] == '1':#卖一价
                self.sellPrice = v[1]
            if v[0] == '2':
                self.tradePrice = v[1]
    #得到服务器数据信息
    def decodeData(self,message):
        # print '获取到了数据'
        strmsg = message.toString().encode('utf8')   #文本作utf8编码
        msgType = message.getHeader().getString(MsgType.FIELD)
        # print msgType
        self.decodePriceData(strmsg)

    #请求一次市场行情数据快照
    def marketOneceTicker(self):
        def requestThreadFunc(obj):
            message = None
            #//get 1000 latest open orders,批量定单查询
            dataRequest = BTCCMarketDataRequest()
            try:
                message = dataRequest.marketDataFullSnapRequest("BTCCNY")
                Session.lookupSession(obj.sessionID).send(message)
            except Exception, e:
                obj.log.info("Exception in trading request: "+str(e))
                raise e

        thtmp = threading.Thread(target=requestThreadFunc,args=(self,))
        thtmp.start()
        thtmp.join()
        print "market data update request once:" + str(self.sessionID)

    #取消市场数据即时更新
    def cancelMarketDataUpdate(self):
        def requestThreadFunc(obj):
            message = None
            #//get 1000 latest open orders,批量定单查询
            dataRequest = BTCCMarketDataRequest()
            try:
                message = dataRequest.unsubscribeIncrementalRequest("BTCCNY")
                Session.lookupSession(obj.sessionID).send(message)
                time.sleep(1000)
            except Exception, e:
                obj.log.info("Exception in trading request: "+str(e))
                raise e

        thtmp = threading.Thread(target=requestThreadFunc,args=(self,))
        thtmp.start()
        thtmp.join()
        print "stop market data update request :" + str(self.sessionID)
    
if __name__ == '__main__':
    account = AccountManger(None,None,None,None)