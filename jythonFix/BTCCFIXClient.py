#!/usr/local/bin/jython
#coding:utf-8
import sys




sys.path.append("lib/backport-util-concurrent-3.0.jar")
sys.path.append("lib/dom4j-1.6.1.jar")
sys.path.append("lib/jcl-over-slf4j-1.6.3.jar")
sys.path.append("lib/log4j-1.2.14.jar")
sys.path.append("lib/mina-core-1.0.3.jar")
sys.path.append("lib/mina-filter-ssl-1.0.3.jar")
sys.path.append("lib/mx4j-3.0.2.jar")
sys.path.append("lib/protobuf-java-2.5.0.jar")
sys.path.append("lib/proxool-0.9.0RC2.jar")
sys.path.append("lib/quickfixj-all-1.5.3.jar")
sys.path.append("lib/sleepycat-je_2.1.30.jar")
sys.path.append("lib/slf4j-api-1.6.3.jar")
sys.path.append("lib/slf4j-log4j12-1.6.3.jar")
sys.path.append("util")
sys.path.append("data")

print sys.path

import AccountManger as AccountManger
import BTCCFIXClientApp

import java.io.IOException as IOException
import java.io.InputStream as InputStream
import quickfix.ConfigError as ConfigError
import quickfix.DefaultMessageFactory as DefaultMessageFactory
import quickfix.DoNotSend as DoNotSend
import quickfix.FileLogFactory as FileLogFactory
import quickfix.FileStoreFactory as FileStoreFactory
import quickfix.Initiator as Initiator
import quickfix.LogFactory as LogFactory
import quickfix.MessageFactory as MessageFactory
import quickfix.MessageStoreFactory as MessageStoreFactory
import quickfix.SessionNotFound as SessionNotFound
import quickfix.SessionSettings as SessionSettings
import quickfix.SocketInitiator as SocketInitiator

# /**
#  * BTCChina FIX API Client 
#  * @author BTCChina
#  */
class BTCCFIXClient():
    def __init__(self):
        pass
    def mainRun(self):
        app = BTCCFIXClientApp.BTCCFIXClientApp()
        inputStream = open('data/quickfix-client.properties','r') #self.getResourceAsStream("/data/quickfix-client.properties")
        settings = SessionSettings(inputStream)
        storeFactory = FileStoreFactory(settings)
        logFactory = FileLogFactory(settings)
        messageFactory = DefaultMessageFactory()
        initiator = SocketInitiator(app, storeFactory, settings, logFactory, messageFactory)
        initiator.block()

if __name__ == '__main__':
    btccclient = BTCCFIXClient()
    btccclient.mainRun()
