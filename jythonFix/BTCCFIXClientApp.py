#!/usr/local/bin/jython
#coding:utf-8

import java.io.IOException as IOException

import org.apache.log4j.Logger as Logger

import util.AccountManger as AccountManger
import util.AccountMangerTest as AccountMangerTest
import util.IniReader as IniReader

import quickfix.DoNotSend as DoNotSend
import quickfix.FieldNotFound as FieldNotFound
import quickfix.IncorrectDataFormat as IncorrectDataFormat
import quickfix.IncorrectTagValue as IncorrectTagValue
import quickfix.RejectLogon as RejectLogon
import quickfix.Session as Session
import quickfix.SessionID as SessionID
import quickfix.UnsupportedMessageType as UnsupportedMessageType


import threading
# /**
#  * BTCChina FIX Client
#  * @author BTCChina
#  */
class BTCCFIXClientApp(quickfix.Application):
    def __init__(self):
        self.log = Logger.getLogger(BTCCFIXClientApp)
    
        self.inireader = initConfig("config.txt");
        self.isTest = True   #是否以测试方式运行
        
        self.runType = 1    #//程序运行方式,1.LTCCNY现货,2.BTCCNY现货,3.BTCLTC现货,4.BTCCNY期货
    
        self.priceStep = float(inireader.getValue("config", "PriceStep"))       #//价格梯度
        self.oneCount = float(inireader.getValue("config", "PriceStep"))        #单次交易量
        self.offset = float(inireader.getValue("config", "OffSet"))             #价格移动
        self.priceStep = float(inireader.getValue("config", "PriceStep"))       #价格梯度

        self.accKey = str(inireader.getValue("config", "acckey"))               #api接口
        self.seckey = str(inireader.getValue("config", "seckey"))               #api密钥

        self.account = None
        self.accountTest = None
    
    def fromAdmin(self,msg,sessionID):
        self.log.info("receivedType:"+msg.getHeader().getString(35))
        self.log.info(sessionID + "------ fromAdmin--------" + msg.toString())
    

    def initConfig(self, configname2):
        # // TODO Auto-generated method stub
        tmp = IniReader(configname2)
        return tmp

    def fromApp(self,msg,sessionID):
        try:
            if self.isTest:
                if self.accountTest == None:
                    self.accountTest = AccountMangerTest(sessionID,self.priceStep,self.oneCount,self.offset,self.accKey,self.secKey)
                    print "config--->" + str(self.priceStep) + "," + str(self.oneCount)
                self.accountTest.decodeData(msg)
            else:
                if self.account == None:
                    self.account = AccountManger(sessionID,self.priceStep,self.oneCount)
                    print "config--->" + str(self.priceStep) + "," + str(self.oneCount)
                self.account.decodeData(msg)
        except Exception, e:
            self.log.warn("In BTCCFIXClientApp::fromApp(quickfix.Message msg, SessionID sessionID)::"+ex.getMessage())
            try:
                if self.isTest:
                    if self.accountTest == None:
                        self.accountTest = AccountMangerTest(sessionID,self.priceStep,self.oneCount,self.offset,self.accKey,self.secKey)
                        print "config--->" + str(self.priceStep) + "," + str(self.oneCount)
                    self.accountTest.decodeData(msg)
                else:
                    if self.account == None:
                        self.account = AccountManger(sessionID,self.priceStep,self.oneCount)
                        print "config--->" + str(self.priceStep) + "," + str(self.oneCount)
                    self.account.decodeData(msg)
            except Exception, e:
                print e
                raise e
    def onCreate(self,sessionID):
        try:
            Session.lookupSession(sessionID).reset()
        except Exception, e:
            raise e
        self.log.info(str(sessionID)+"------ onCreate Session-------"+str(sessionID))

    def onLogon(self,sessionID):
        def logonthreadrun(sid):
            message = BTCCMarketDataRequest.myMarketData("BTCCNY")
            Session.lookupSession(sid).send(message)
            try:
                sleep(5000)
            except Exception, e:
                print e
                raise e
        thtmp = threading.Thread(target=logonthreadrun,args=(sessionID,))
        thtmp.start()
        thtmp.join()

        self.log.info(str(sessionID) + "------ onLogon-------" + str(sessionID));
    
    def onLogout(self, sessionID):
        self.log.info(str(sessionID) + "------ onLogout-------" + str(sessionID))

    def toAdmin(msg,sessionID):
        self.log.info(str(sessionID) + "------ toAdmin-------" + str(sessionID))

    def toApp(msg,sessionID):
        self.log.info(str(sessionID) + "------ toApp-------" + str(sessionID))

