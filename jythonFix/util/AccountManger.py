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

class AccountManger():
    def __init__(self,pID,pStepPrice,pTradeCount,plog):
        self.log = plog #Logger.getLogger(AccountManger)      #//log输出工具
        self.dataDict = DataDictionary("data/selfFIX44.xml")                            #//new DataDictionary("FIX44.xml"); //fix4.4协议
        self.msgPrinter = MessagePrinter.MessagePrinter()
        self.sessionID = pID                           #//fix绘话ID
        #买一
        self.buyOneCount = 0.0                          #//买一价数量
        self.buyOnePrice = 0.0                          #买一价
        #卖一
        self.sellOneCount = 0.0                         #卖一价数量
        self.sellOnePrice = 0.0                         #卖一价
    
        #最新成交价
        self.nowTradePrice = 0.0                        #最新成交价

        #触发价
        self.lastSetpPrice = 0.0                        #上次梯度价格
        self.nextBuyPrice = 0.0                         #下次触发买单价
        self.nextSellPrice = 0.0                        #下次解发卖单价

        #帐户初始化
        self.baseMoney = 0.0                            #起始资金来自帐户数据获取
        self.priceStep = float(pStepPrice)                            #解发价格梯度
        self.tradeCount = float(pTradeCount)                           #单次交易量
    
        #帐户实时更新数据
        self.heaveMoney = 0.0                           #当前货币量
        self.heaveGood = 0.0                            #当前物品量
        self.allRes = 0.0                               #当前总资产数量
        self.nowPrice = 0.0                             #当前成成交价,当获取到的最新成交价不在买一卖一之内时，最新成交价使用买一价与卖一价的中间值,此值不参与交易运算，只作收益统计
        self.yieldRate = 0.0                            #收效率=(allRes/baseMoney)*100%
    
        #帐户挂单冻结信息
        self.iceMoney = 0.0                             #冻结货币
        self.iceGood = 0.0                              #冻结物品
    
        #log记录
        self.tradeBuyCount = 0                          #交易购买次数
        self.tradeSellCount = 0                         #交易出售次数
        self.outRangeMoneyCount = 0                     #交易无货币次数
        self.outRangeGoodCount = 0                      #交易无物品次数
        self.maxPrice = 0.0                             #系统运行到现在的市场最大成交价
        self.minPrice = 0.0                             #系统运行到现在的市场最小成交价
    
        #交易
        self.sellOrderID = ""                           #出信定单挂单ID
        self.sellOrderType = 0                          #出售定单状态,0.未下单,1.正在挂单,2.部分成交
    
        self.buyOrderID = ""                            #购买定单挂单ID
        self.buyOrderType = 0                           #购买定单状态,0.未下单,1.正在挂单,2.部分成交
    
        self.lastTradePrice = 0.0                       #上次定单成交价,不作运算，只作分析用
        self.continuityBuyTimes = 0                     #连续购买次数,只作分析用
        self.continuitySellTimes = 0                    #连续出购次数,只作分析用
        self.continuityOutRanceMonye = 0                #连续无货币次数,用来提示价格暴涨
        self.continuityOutRanceGood = 0                 #连续无物品次数,用来提示价格暴跌
    
        #挂单信息
        self.orderIDs = []                              #已下单，但未完全成交的订单ID
        #市场数据状态
        self.isReqMarkDataUpdate = True                 #是否开启市场数据更新
    
        #初始化
        # self.getAccountData()
        # self.orderCheckAll()

    
    #获取帐户信息
    def getAccountData(self):
        def requestThreadFunc(obj):
            message = None
            ACCESS_KEY = ""
            SECRET_KEY = ""
            tradeRequest = BTCCTradingRequest()
            try:
                message = tradeRequest.createUserAccountRequest(ACCESS_KEY, SECRET_KEY)
                Session.lookupSession(obj.sessionID).send(message)
            except Exception, e:
                obj.log.info("Exception in trading request: "+str(e))
                raise e

        thtmp = threading.Thread(target=requestThreadFunc,args=(self,))
        thtmp.start()
        thtmp.join()
        self.log.info("getAccountData-------"+str(sessionID))
    
    
    def accountfunc(self,fieldMap):
        fieldIterator = fieldMap.iterator()
        fname = ""
        while fieldIterator.hasNext():
            field = fieldIterator.next()
            if not self.isGroupCountField(field):
                tagstr = ""
                try:
                    tagstr = fieldMap.getString(field.getTag())
                    value = tagstr
                    if self.dataDict.hasFieldValue(field.getTag()):
                        value = dataDict.getValueName(field.getTag(),tagstr)
                    if self.dataDict.getFieldName(field.getTag()) == "Currency":
                        fname = value
                    elif self.dataDict.getFieldName(field.getTag()) == "Amount":
                        if fname == "BTC":
                            self.heaveGood = float(value)
                            print 'btc=' + str(value)
                        elif fname == "LTC":
                            print 'ltc=' + str(value)
                        elif fname == "CNY":
                            self.heaveMoney = float(value)
                            print "cny=" + str(value)
                except Exception, e:
                    print e
                    raise e

    #设置帐户数据
    def setAccountRes(self,fieldMap):
        groupsKeys = fieldMap.groupKeyIterator()
        while groupsKeys.hasNext():
            groupCountTag = int(groupsKeys.next().intValue())
            groupTagstr = 0
            try:
                groupTagstr = fieldMap.getInt(groupCountTag)
            except Exception, e:
                print e
                raise e
            g = Group(groupCountTag, 0)
            i = 1
            while fieldMap.hasGroup(i,groupCountTag):
                try:
                    fieldMap.getGroup(i,g)
                    self.accountfunc(g)
                except Exception, e:
                    raise e
                i += 1
    

    
    #测试是否可下单
    def testTrade(self):
        tmpprice = 0.5      #下单价与深度价的差值,使交易可以马上成交
        if math.abs((self.buyOnePrice - self.lastSetpPrice) - tmpprice) > self.priceStep and self.buyOnePrice > self.lastSetpPrice:
            if self.heaveGood >= self.tradeCount:
                print 'sell-------->'
                #self.sell(self.buyOnePrice - tmpprice) #价格上涨了作出售操作，如售前要先看之前的定单是否有成交,没有则取消
        elif math.asb((self.lastSetpPrice - self.sellOnePrice)-tmpprice) > self.priceStep and self.lastSetpPrice > self.sellOnePrice:
            buytmp = self.sellOnePrice + tmpprice
            if self.heaveMoney >= self.tradeCount * buytmp:
                #//货币够，可以作买入操作
                print 'buy---------->'
                #self.buy(buytmp)                        #//价格下跌了作出售操作，如售前要先看之前的定单是否有成交,没有则取消
    
    
    #即时行情数据数组处理
    def marketDatarefreshtField(self,fieldMap):
        fieldIterator = fieldMap.iterator()
        tname = ""
        while fieldIterator.hasNext():
            field = fieldIterator.next()
            if not self.isGroupCountField(field):
                value = ""
                try:
                    value = fieldMap.getString(field.getTag())
                    #tname
                    if self.dataDict.hasFieldValue(field.getTag()): 
                        value = self.dataDict.getValueName(field.getTag(), value);
                    #//行情数据
                    if self.dataDict.getFieldName(field.getTag()) == "MDEntryType":
                        tname = value
                    elif self.dataDict.getFieldName(field.getTag()) == "MDEntryType":
                        if tname == "BID":
                            self.buyOnePrice = float(value)  #买一价0
                        elif tname == "OFFER":
                            self.sellOnePrice = float(value) #卖一价
                        elif tname == "TRADE":               #最新成交
                            tmpvalue = float(value)
                            if tmpvalue >= self.buyOnePrice and tmpvalue <= self.sellOnePrice:
                                self.nowTradePrice = tmpvalue
                            else:
                                self.nowTradePrice = (self.buyOnePrice + self.sellOnePrice)/2.0
                except Exception, e:
                    print e
                    raise e
        #测试是否达到下单要求
        self.testTrade();

    #刷新交易数据,买一，卖一，当前成交
    def DataRefresh(self,fieldMap):
        groupsKeys = fieldMap.groupKeyIterator()
        while groupsKeys.hasNext():
            groupCountTag = int(groupsKeys.next().intValue())
            g = Group(groupCountTag, 0)
            i = 1
            while fieldMap.hasGroup(i, groupCountTag):
                if i > 1:
                    print "-----------"
                try:
                    fieldMap.getGroup(i, g)
                    self.marketDatarefreshtField(g)
                except Exception, e:
                    raise e
                i += 1


    #已知定单数据更新，如已成交，或部分成交，或取消成功消息
    def tradeOrderUpdate(self,fieldMap):
        pass

    #定单编号查询定单
    def checkOrderBackWithID(self,fieldMap):
        pass

    #批量定单查询
    def checkOrdersBack(self,fieldMap):
        pass

    #交易购买消息反回
    def tradeBuyOrderBack(self,fieldMap):
        pass

    #交易出售消息反回
    def tradeSellOrderBack(self,fieldMap):
        pass

    #交易取消
    def cancelOrderBack(self,fieldMap):
        pass

    #交易执行报告拒绝
    def tradeExecuteBadBack(self,fieldMap):
        pass

    # //--------------------------------------------------------------------
    # //打开市场数据即时更新
    def openMarketDataUpdate(self):
        def requestThreadFunc(obj):
            message = None
            #//get 1000 latest open orders,批量定单查询
            dataRequest = BTCCMarketDataRequest()
            try:
                message = dataRequest.myMarketData("BTCCNY")
                Session.lookupSession(obj.sessionID).send(message)
            except Exception, e:
                obj.log.info("Exception in trading request: "+str(e))
                raise e

        thtmp = threading.Thread(target=requestThreadFunc,args=(self,))
        thtmp.start()
        thtmp.join()
        print "market data update request:" + str(self.sessionID)

    
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


    #买单下单
    def buy(self,price):
        self.lastSetpPrice = price
        return True


    #卖单下单
    def sell(self,price):
        self.lastSetpPrice = price
        return True

    
    #定单查询,使用已知下单ID查询
    def orderCheck(self,orderID):
        pass

    
    #定单批量查询,查询count个未成交定单
    def orderCheckAll(self):
        def requestThreadFunc(obj):
            message = None
            ACCESS_KEY = ""
            SECRET_KEY = ""
            tradeRequest = BTCCTradingRequest()
            try:
                message = tradeRequest.createOrderMassStatusRequest(ACCESS_KEY, SECRET_KEY,"BTCCNY")
                Session.lookupSession(obj.sessionID).send(message)
                time.sleep(10)
            except Exception, e:
                obj.log.info("Exception in trading request: "+str(e))
                raise e

        thtmp = threading.Thread(target=requestThreadFunc,args=(self,))
        thtmp.start()
        thtmp.join()
        print "orderCheckAll request :" + str(self.sessionID)

    
    
    #取消定单
    def cancelOrder(self, orderID):
        pass
    
    
    #得到服务器数据信息
    def decodeData(self,message):
        print '获取到了数据'
        print message.toString()
        msgType = message.getHeader().getString(MsgType.FIELD)
        print msgType
        self.msgPrinter.mpprint(self.dataDict, message);
        # print "getMsgType:" + str(msgType)
        # if msgType == "X": #市场行情数据即时更新
        #     self.DataRefresh(message)
        # elif msgType == "V": #取消市场行情即时更新
        #     print "hello V"
        # elif msgType == "W": #////市场行情数据快照('W'类型)
        #     self.DataRefresh(message)
        #     print "hello W"
        # elif msgType == "Y": #市场数据请求拒绝
        #     print "hello Y"
        # #帐户请求
        # elif msgType == "U1001": #帐户信息
        #     self.setAccountRes(message)
        #     # self.msgPrinter.print(dataDict, message);
        # elif msgType == "8":     #交易定单,指定定单ID查询,批量定单查询,定单取消
        #     self.getServerDataTag8(message)
        #     # self.msgPrinter.print(dataDict, message)
        # else:
        #     print "msgPrinter print"
        #     # self.msgPrinter.print(dataDict, message);

    #获取交易相关回复
    def getServerDataTag8(self,fieldMap):
        fieldIterator = fieldMap.iterator()
        tname = ""
        while fieldIterator.hasNext():
            if not self.isGroupCountField(field):
                value = ""
                try:
                    value = fieldMap.getString(field.getTag())
                    if self.dataDict.hasFieldValue(field.getTag()):
                        value = self.dataDict.getValueName(field.getTag(), value) + " (" + value + ")"
                    # 批量查询
                    if self.dataDict.getFieldName(field.getTag()) == "MassStatusReqID" and value == ReqConfig.reqAllCheckID:
                        self.checkOrderBackWithID(fieldMap)
                        return
                    # 交易
                    if self.dataDict.getFieldName(field.getTag()) == "ClOrdID":
                        if value == "10001":    #交易购买请求唯一ID
                            self.tradeBuyOrderBack(fieldMap)
                        elif value == "10002":  #交易出售请求唯一ID
                            self.tradeSellOrderBack(fieldMap)
                        elif value == "10003":  #交易购买市价单请求唯一ID
                            self.tradeBuyOrderBack(fieldMap)
                        elif value == "10004":  #交易出售市价单请求唯一ID
                            self.tradeSellOrderBack(fieldMap)
                        elif value == "10005":  #已知定单号查询唯一ID
                            self.checkOrderBackWithID(fieldMap) 
                        elif value == "10006":  #批量查询唯一ID
                            print "10006"
                        elif value == "10007":  #取消订单请求唯一ID
                            self.cancelOrderBack(fieldMap) 
                        elif value == "10008":  #服务器执行报告拒绝唯一ID
                            self.tradeExecuteBadBack(fieldMap) 
                        else:
                            # self.msgPrinter.print(dataDict, (quickfix.fix44.Message)fieldMap)
                            print "msgPrinter fieldMap"
                        return
                except Exception, e:
                    print "erro getServerDataTag8:" + str(e)
                    raise e
    
    def printFieldMap(self,prefix,msgType,fieldMap):
        fieldIterator = fieldMap.iterator()
        while fieldIterator.hasNext():
            field = fieldIterator.next()
            if not self.isGroupCountField(field):
                value = fieldMap.getString(field.getTag())
                if self.dataDict.hasFieldValue(field.getTag()):
                    value = self.dataDict.getValueName(field.getTag(), fieldMap.getString(field.getTag())) + " (" + value + ")"
                print prefix + dataDict.getFieldName(field.getTag()) + ": " + value

        groupsKeys = fieldMap.groupKeyIterator()
        while groupsKeys.hasNext():
            groupCountTag = int(groupsKeys.next())
            print prefix + dataDict.getFieldName(groupCountTag) + ": count = " + fieldMap.getInt(groupCountTag)
            g = Group(groupCountTag, 0)
            i = 1
            while fieldMap.hasGroup(i, groupCountTag):
                if i > 1:
                    print prefix + "  ----"
                fieldMap.getGroup(i, g)
                self.printFieldMap(prefix + "  ",msgType, g)
                i += 1

    def isGroupCountField(self,field):
        return self.dataDict.getFieldTypeEnum(field.getTag()) == FieldType.NumInGroup

