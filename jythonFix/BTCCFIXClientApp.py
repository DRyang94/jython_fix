#!/usr/local/bin/jython
#coding:utf-8
import java
import javax

import java.io.IOException as IOException

import org.apache.log4j.Logger as Logger

import AccountManger
import IniReader as IniReader

import quickfix.DoNotSend as DoNotSend
import quickfix.FieldNotFound as FieldNotFound
import quickfix.IncorrectDataFormat as IncorrectDataFormat
import quickfix.IncorrectTagValue as IncorrectTagValue
import quickfix.RejectLogon as RejectLogon
import quickfix.Session as Session
import quickfix.SessionID as SessionID
import quickfix.UnsupportedMessageType as UnsupportedMessageType

import quickfix.Application as Application

import threading
import BTCCMarketDataRequest

import time
# /**
#  * BTCChina FIX Client
#  * @author BTCChina
#  */
class BTCCFIXClientApp(Application):
    def __init__(self):
        Application.__init__(self)
        self.log = Logger.getLogger(Application)
    
        self.inireader = self.initConfig("data/config.txt");
        self.isTest = True   #是否以测试方式运行
        
        self.runType = 1    #//程序运行方式,1.LTCCNY现货,2.BTCCNY现货,3.BTCLTC现货,4.BTCCNY期货
    
        self.priceStep = float(self.inireader.getValue("config", "PriceStep"))       #//价格梯度
        self.oneCount = float(self.inireader.getValue("config", "PriceStep"))        #单次交易量
        self.offset = float(self.inireader.getValue("config", "OffSet"))             #价格移动
        self.priceStep = float(self.inireader.getValue("config", "PriceStep"))       #价格梯度

        self.accKey = str(self.inireader.getValue("config", "acckey"))               #api接口
        self.seckey = str(self.inireader.getValue("config", "seckey"))               #api密钥

        self.account = None
        self.accountTest = None
    
    def fromAdmin(self,msg,sessionID):
        self.log.info("receivedType:"+msg.getHeader().getString(35))
        self.log.info(str(sessionID) + "------ fromAdmin--------" + msg.toString())
        print "aaaaaa"
        print msg.toString()
    

    def initConfig(self, configname2):
        # // TODO Auto-generated method stub
        tmp = IniReader.IniReader(configname2)
        return tmp

    def fromApp(self,msg,sessionID):
        self.log.info(str(sessionID) + "------ fromApp--------" + msg.toString())
        if self.account == None:
            self.account = AccountManger.AccountManger(str(sessionID),self.priceStep,self.oneCount,self.log)
        self.account.decodeData(msg)

    def onCreate(self,sessionID):
        print 'id======>',sessionID
        try:
            Session.lookupSession(sessionID).reset()
        except Exception, e:
            raise e
        self.log.info(str(sessionID)+"------ onCreate Session-------"+str(sessionID))

    def onLogon(self,sessionID):
        print 'sessionID----->',sessionID
        def logonthreadrun(sid):
            marketreauest = BTCCMarketDataRequest.BTCCMarketDataRequest()
            # message = marketreauest.myMarketData("BTCCNY")
            message = marketreauest.myMarketData("LTCCNY")
            Session.lookupSession(sid).send(message)
            print "sid------>",sid
            try:
                time.sleep(5)
            except Exception, e:
                print e
                raise e
        thtmp = threading.Thread(target=logonthreadrun,args=(sessionID,))
        thtmp.start()
        thtmp.join()

        self.log.info(str(sessionID) + "------ onLogon-------" + str(sessionID));
    
    def onLogout(self, sessionID):
        self.log.info(str(sessionID) + "------ onLogout-------" + str(sessionID))

    def toAdmin(self,msg,sessionID):
        print msg
        self.log.info(str(sessionID) + "------ toAdmin-------" + str(sessionID))

    def toApp(self,msg,sessionID):
        self.log.info(str(sessionID) + "------ toApp-------" + str(sessionID))

