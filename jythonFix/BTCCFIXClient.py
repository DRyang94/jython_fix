
import sys
import util.AccountMangerTest as AccountMangerTest
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
		self.isTest = False  #是否以测试方式运行
		self.main()
	def main(self):
		if self.isTest:
			testobj = AccountMangerTest(None,1.62,0.0,0.0,True)
			testobj.projectTest()
		else:
			app = BTCCFIXClientApp()
			inputStream = self.getResourceAsStream("/quickfix-client.properties")
			settings = SessionSettings(inputStream)
			storeFactory = FileStoreFactory(settings)
			logFactory = FileLogFactory(settings)
			messageFactory = DefaultMessageFactory()
			initiator = SocketInitiator(app, storeFactory, settings, logFactory, messageFactory)
			initiator.block()
