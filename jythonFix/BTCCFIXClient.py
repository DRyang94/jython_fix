package com.btcchina.fix;

import com.btcchina.fix.util.AccountMangerTest;

import java.io.IOException;
import java.io.InputStream;
import quickfix.ConfigError;
import quickfix.DefaultMessageFactory;
import quickfix.DoNotSend;
import quickfix.FileLogFactory;
import quickfix.FileStoreFactory;
import quickfix.Initiator;
import quickfix.LogFactory;
import quickfix.MessageFactory;
import quickfix.MessageStoreFactory;
import quickfix.SessionNotFound;
import quickfix.SessionSettings;
import quickfix.SocketInitiator;

/**
 * BTCChina FIX API Client 
 * @author BTCChina
 */
class BTCCFIXClient():
	def function(self):
		pass

	static public boolean isTest = false;	//是否以测试方式运行
	
	public static void main(String args[]) throws ConfigError, DoNotSend, IOException, SessionNotFound, InterruptedException{
		if(BTCCFIXClient.isTest)
		{
			AccountMangerTest testobj = new AccountMangerTest(null, 1.62f, 0.01f, 0.8f,true);
			testobj.projectTest();
		}else{
			BTCCFIXClientApp app = new BTCCFIXClientApp();
		    InputStream inputStream = BTCCFIXClient.class.getResourceAsStream("/quickfix-client.properties");
		    SessionSettings settings = new SessionSettings(inputStream);
		    MessageStoreFactory storeFactory = new FileStoreFactory(settings);
		    LogFactory logFactory = new FileLogFactory(settings);
		    MessageFactory messageFactory = new DefaultMessageFactory();
		    Initiator initiator = new SocketInitiator(app, storeFactory, settings, logFactory, messageFactory);
		    initiator.block();
		}
	}
}
