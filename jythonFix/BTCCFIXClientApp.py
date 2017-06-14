

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

# /**
#  * BTCChina FIX Client
#  * @author BTCChina
#  */
class BTCCFIXClientApp  implements quickfix.Application {
	private static final Logger log = Logger.getLogger(BTCCFIXClientApp.class);
	
	private IniReader inireader = initConfig("config.txt");
	
	private boolean isTest = true;	//是否以测试方式运行
	
	private int runType = 1;	//程序运行方式,1.LTCCNY现货,2.BTCCNY现货,3.BTCLTC现货,4.BTCCNY期货
	
	private float priceStep = Float.valueOf(inireader.getValue("config", "PriceStep")); 	//价格梯度
	private float oneCount = Float.valueOf(inireader.getValue("config", "OnceCount"));	//单次交易量
	private float offset = Float.valueOf(inireader.getValue("config", "OffSet"));	//单次交易量
	
	private String accKey = String.valueOf(inireader.getValue("config", "acckey"));	//单次交易量
	private String secKey = String.valueOf(inireader.getValue("config", "seckey"));	//单次交易量
	
	
	private AccountManger account = null;
	private AccountMangerTest accountTest = null;
	
	public void fromAdmin(quickfix.Message msg, SessionID sessionID)
			throws FieldNotFound, IncorrectDataFormat, IncorrectTagValue, RejectLogon {
		log.info("receivedType:"+msg.getHeader().getString(35));
		log.info(sessionID+"------ fromAdmin--------"+msg.toString());
	}

	private IniReader initConfig(String configname2) {
		// TODO Auto-generated method stub
		
		try {
			IniReader tmp = new IniReader(configname2);
			return tmp;
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return null;
	}

	public void fromApp(quickfix.Message msg, SessionID sessionID)
			throws FieldNotFound, IncorrectDataFormat, IncorrectTagValue, UnsupportedMessageType {

		//log.info("receivedType:"+msg.getHeader().getString(35));
		//log.info(sessionID+"------ fromApp---------"+msg.toString());
		
	     try
         {
	    	 if(isTest){
	    		 if(accountTest == null)
		    	 {
		    		 accountTest = new AccountMangerTest(sessionID,priceStep,oneCount,offset,accKey,secKey);
		    		 System.out.println("config--->"+priceStep+","+oneCount);
		    	 }
		    	 accountTest.decodeData((quickfix.fix44.Message)msg);
	    	 }else{
	    		 if(account == null)
		    	 {
	    			 account = new AccountManger(sessionID,priceStep,oneCount);
	    			 System.out.println("config--->"+priceStep+","+oneCount);
		    	 }
	    		 account.decodeData((quickfix.fix44.Message)msg);
	    	 }
	    	 
         }	     
         catch (Exception ex)
         {
        	 log.warn("In BTCCFIXClientApp::fromApp(quickfix.Message msg, SessionID sessionID)::"+ex.getMessage());
 	    	 try {
 	    		if(isTest){
 		    		 if(accountTest == null)
 			    	 {
 			    		 accountTest = new AccountMangerTest(sessionID,priceStep,oneCount,offset,accKey,secKey);
 			    		System.out.println("config--->"+priceStep+","+oneCount);
 			    	 }
 			    	 accountTest.decodeData((quickfix.fix44.Message)msg);
 		    	 }else{
 		    		 if(account == null)
 			    	 {
 		    			 account = new AccountManger(sessionID,priceStep,0.06f);
 		    			System.out.println("config--->"+priceStep+","+oneCount);
 			    	 }
 		    		 account.decodeData((quickfix.fix44.Message)msg);
 		    	 }
 	    	 } catch (Exception e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
         }
	}

	public void onCreate(SessionID sessionID) {
		try {
			//there should invoke reset()
			Session.lookupSession(sessionID).reset();
		} catch (IOException e) {
			e.printStackTrace();
		}
		log.info(sessionID+"------ onCreate Session-------"+sessionID);
	}
	
	public void onLogon(final SessionID sessionID) {
		
		new Thread(new Runnable() {
			@Override
			public void run() {
				quickfix.Message message;

				// MARKET DATA INCREMENTAL REFRESH REQUEST (V)
//				message = BTCCMarketDataRequest.marketDataIncrementalRequest("LTCBTC");	
//				message = BTCCMarketDataRequest.marketDataIncrementalRequest("LTCCNY");	
//				message = BTCCMarketDataRequest.marketDataIncrementalRequest("BTCCNY");	
//				Session.lookupSession(sessionID).send(message);				
//				try {
//					Thread.sleep(5000);
//				} catch (InterruptedException e) {
//					// TODO Auto-generated catch block
//					e.printStackTrace();
//				}
					
				//MARKET DATA SNAPSHOT FULL REFRESH REQUEST (V)
				//message = BTCCMarketDataRequest.marketDataFullSnapRequest("LTCCNY");
//				message = BTCCMarketDataRequest.marketDataIncrementalRequest("BTCCNY");	
//				Session.lookupSession(sessionID).send(message);		
//				try {
//					Thread.sleep(1000);
//				} catch (InterruptedException e) {
//					// TODO Auto-generated catch block
//					e.printStackTrace();
//				}
				
				//市场数据即时更新
				message = BTCCMarketDataRequest.myMarketData("BTCCNY");	
				Session.lookupSession(sessionID).send(message);
				try {
					Thread.sleep(3000);
				} catch (InterruptedException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
				
				
//				UNSUBSCRIBE MARKET DATA INCREMENTAL REFRESH (V)
//				message = BTCCMarketDataRequest.unsubscribeIncrementalRequest("LTCCNY");	
//				message = BTCCMarketDataRequest.marketDataIncrementalRequest("BTCCNY");	
//				Session.lookupSession(sessionID).send(message);
//				try {
//					Thread.sleep(3000);
//				} catch (InterruptedException e) {
//					// TODO Auto-generated catch block
//					e.printStackTrace();
//				}
				
//				String ACCESS_KEY = "<YOUR ACCESS KEY>";
//			    String SECRET_KEY = "<YOUR SECRET KEY>";
//			    
//			    BTCCTradingRequest tradeRequest=new BTCCTradingRequest();
//			    try{
				    
				    //limit order on market BTCCNY/LTCCNY/LTCBTC
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.SELL, OrdType.LIMIT, 10000, 0.0001, "BTCCNY"); // integer not supported??
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.SELL, OrdType.LIMIT, 1001.1, 2.1, "BTCCNY"); //
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.BUY, OrdType.LIMIT, 1000, 0.0001, "BTCCNY"); //
				    
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.SELL, OrdType.LIMIT, 1001.1, 0.001, "LTCCNY"); //
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.BUY, OrdType.LIMIT, 1, 0.001, "LTCCNY"); //
			    	
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.SELL, OrdType.LIMIT, 1001.1, 0.001, "LTCBTC"); //
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.BUY, OrdType.LIMIT, 0.0001, 0.001, "LTCBTC"); //
				    
				    //market order sell/buy
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.SELL, OrdType.MARKET, 0.0001d, "BTCCNY");
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.BUY, OrdType.MARKET, 0.0001d, "BTCCNY");
			    	
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.SELL, OrdType.MARKET, 0.001d, "LTCCNY");
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.BUY, OrdType.MARKET, 0.001d, "LTCCNY");
			    	
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.SELL, OrdType.MARKET, 0.001d, "LTCBTC");
//				    message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.BUY, OrdType.MARKET, 0.001d, "LTCBTC");
				    
			    	// cancel an order
//				    message = tradeRequest.createOrderCancelRequest(ACCESS_KEY, SECRET_KEY, 42664407, "BTCCNY");
			    	
			    	//get account info
//				    message = tradeRequest.createUserAccountRequest(ACCESS_KEY, SECRET_KEY);
			    	
			    	//get order
////				    message = tradeRequest.createOrderStatusRequest(ACCESS_KEY, SECRET_KEY, "BTCCNY",42663920);
//				    
//				    //get 1000 latest open orders
//				    message = tradeRequest.createOrderMassStatusRequest(ACCESS_KEY, SECRET_KEY,"BTCCNY");
//				    
//				    Session.lookupSession(sessionID).send(message);
//			    } catch (Exception e){
//			    	log.info("Exception in trading request: "+e.toString());
//			    }
			}
		}).start();
		
		log.info(sessionID+"------ onLogon-------"+sessionID);
	}

	public void onLogout(SessionID sessionID) {
		log.info(sessionID+"------ onLogout -------"+sessionID);
	}

	public void toAdmin(quickfix.Message msg, SessionID sessionID) {
		log.info(sessionID+"------ toAdmin---------"+msg.toString());
	}

	public void toApp(quickfix.Message msg, SessionID sessionID) throws DoNotSend {
		log.info(sessionID+"------ toApp-----------"+msg.toString());
	}
}
