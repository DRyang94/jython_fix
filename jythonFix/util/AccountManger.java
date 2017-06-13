package com.btcchina.fix.util;

import java.util.Iterator;
import java.util.LinkedList;
import java.lang.Math;

import org.apache.log4j.Logger;

import com.btcchina.fix.BTCCMarketDataRequest;
import com.btcchina.fix.BTCCTradingRequest;

import quickfix.ConfigError;
//import javax.xml.parsers.DocumentBuilderFactory;
//import javax.xml.parsers.DocumentBuilder;
//
//import org.w3c.dom.Document;
//import org.w3c.dom.NodeList;
//import org.w3c.dom.Node;
//import org.w3c.dom.Element;
import quickfix.DataDictionary;
import quickfix.Field;
import quickfix.FieldMap;
import quickfix.FieldNotFound;
import quickfix.FieldType;
import quickfix.Group;
import quickfix.Session;
import quickfix.SessionID;
import quickfix.field.MsgType;
import quickfix.fix44.Message;

public class AccountManger {
	private static final Logger log = Logger.getLogger(AccountManger.class);	//log输出工具
	private DataDictionary dataDict = null;//new DataDictionary("FIX44.xml");	//fix4.4协议
	private MessagePrinter msgPrinter = null;
	public SessionID sessionID = null;		//fix绘话ID
	
	//买一
	public float buyOneCount = 0.0f;		//买一价数量
	public float buyOnePrice = 0.0f;		//买一价
	
	//卖一
	public float sellOneCount = 0.0f;		//卖一价数量
	public float sellOnePrice = 0.0f;		//卖一价
	//最新成交价
	public float nowTradePrice = 0.0f;		//最新成交价
	
	//解发价
	public float lastSetpPrice = 0.0f; 		//上次梯度价格
	public float nextBuyPrice = 0.0f;		//下次触发买单价
	public float nextSellPrice = 0.0f;		//下次解发卖单价
	
	//帐户初始化
	public float baseMoney = 0.0f;			//起始资金来自帐户数据获取
	public float priceStep = 0.0f;			//解发价格梯度
	public float tradeCount = 0.0f;			//单次交易量
	
	//帐户实时更新数据
	public float heaveMoney = 0.0f;			//当前货币量
	public float heaveGood = 0.0f;			//当前物品量
	public float allRes = 0.0f;				//当前总资产数量
	public float nowPrice = 0.0f;			//当前成成交价,当获取到的最新成交价不在买一卖一之内时，最新成交价使用买一价与卖一价的中间值,此值不参与交易运算，只作收益统计
	public float yieldRate = 0.0f;			//收效率=(allRes/baseMoney)*100%
	
	//帐户挂单冻结信息
	public float iceMoney = 0.0f;			//冻结货币
	public float iceGood = 0.0f;			//冻结物品
	
	//log记录
	public int tradeBuyCount = 0;			//交易购买次数
	public int tradeSellCount = 0;			//交易出售次数
	public int outRangeMoneyCount = 0;		//交易无货币次数
	public int outRangeGoodCount = 0;		//交易无物品次数
	public float maxPrice = 0.0f;			//系统运行到现在的市场最大成交价
	public float minPrice = 0.0f;			//系统运行到现在的市场最小成交价
	
	//交易
	public String sellOrderID = "";			//出信定单挂单ID
	public int sellOrderType = 0;			//出售定单状态,0.未下单,1.正在挂单,2.部分成交
	
	public String buyOrderID = "";			//购买定单挂单ID
	public int buyOrderType = 0;			//购买定单状态,0.未下单,1.正在挂单,2.部分成交
	
	public float lastTradePrice = 0.0f;		//上次定单成交价,不作运算，只作分析用
	public int continuityBuyTimes = 0;		//连续购买次数,只作分析用
	public int continuitySellTimes = 0;		//连续出购次数,只作分析用
	public int continuityOutRanceMonye = 0;	//连续无货币次数,用来提示价格暴涨
	public int continuityOutRanceGood = 0;	//连续无物品次数,用来提示价格暴跌
	
	//挂单信息
	private LinkedList<String> orderIDs = new LinkedList<String>(); //已下单，但未完全成交的订单ID
	//市场数据状态
	private boolean isReqMarkDataUpdate = true;		//是否开启市场数据更新
	
	//初始化
	public AccountManger(SessionID pID,float pStepPrice,float pTradeCount) {
		
		this.priceStep = pStepPrice;		//初始化价格梯度
        this.tradeCount = pTradeCount;		//初始化单次交易量
        this.sessionID = pID;				//fix绘话ID
        
        if(msgPrinter == null){
        	msgPrinter = new MessagePrinter();
        }
        if(dataDict == null)
        {
        	try {
            	dataDict = new DataDictionary("selfFIX44.xml");
    		} catch (ConfigError e) {
    			// TODO Auto-generated catch block
    			e.printStackTrace();
    		}
        }
        getAccountData();
        orderCheckAll();
    }
	
	//获取帐户信息
	private void getAccountData()
	{
		new Thread(new Runnable() {
			@Override
			public void run() {
				quickfix.Message message;
				
				String ACCESS_KEY = "";
			    String SECRET_KEY = "";
			    
			    BTCCTradingRequest tradeRequest=new BTCCTradingRequest();
			    try{
			    	//get account info
				    message = tradeRequest.createUserAccountRequest(ACCESS_KEY, SECRET_KEY);

				    Session.lookupSession(sessionID).send(message);
			    } catch (Exception e){
			    	log.info("Exception in trading request: "+e.toString());
			    }
			}
		}).start();
		
		log.info("getAccountData-------"+sessionID);
	}
	
	private void accountfunc(FieldMap fieldMap)
	{
		Iterator<?> fieldIterator = fieldMap.iterator();
		String fname = "";
        while (fieldIterator.hasNext()) {
            Field<?> field = (Field<?>) fieldIterator.next();
            if (!isGroupCountField(field)) {
            	String tagstr = "";
				try {
					tagstr = fieldMap.getString(field.getTag());
					String value = tagstr;
	                if (dataDict.hasFieldValue(field.getTag())) {
	                    value = dataDict.getValueName(field.getTag(), tagstr);
	                }
	                if(dataDict.getFieldName(field.getTag()).compareTo("Currency") == 0)
	                {
	                	fname = value;
	                }else if(dataDict.getFieldName(field.getTag()).compareTo("Amount") == 0)
	                {
	                	switch(fname)
	                	{
	                	case "BTC":
	                	{
	                		this.heaveGood = Float.valueOf(value);
	                		System.out.println("btc=" + value);
	                	}
	                	break;
	                	case "LTC":
	                	{
	                		System.out.println("ltc=" + value);
	                	}
	                	break;
	                	case "CNY":
	                	{
	                		this.heaveMoney = Float.valueOf(value);
	                		System.out.println("cny=" + value);
	                	}
	                	break;
	                	default:
	                		break;
	                	}
	                }
				} catch (FieldNotFound e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
            }
        }
	}
	//设置帐户数据
	private void setAccountRes(FieldMap fieldMap)
	{
        Iterator<?> groupsKeys = fieldMap.groupKeyIterator();
        while (groupsKeys.hasNext()) {
            int groupCountTag = ((Integer) groupsKeys.next()).intValue();
            int groupTagstr;
			try {
				groupTagstr = fieldMap.getInt(groupCountTag);
			} catch (FieldNotFound e1) {
				// TODO Auto-generated catch block
				e1.printStackTrace();
			}
            Group g = new Group(groupCountTag, 0);
            int i = 1;
            while (fieldMap.hasGroup(i, groupCountTag)) {
                try {
					fieldMap.getGroup(i, g);
					accountfunc(g);
				} catch (FieldNotFound e) {
					e.printStackTrace();
				}
                i++;
            }
        }
	}
	
	
	private void testLastTrade()
	{
		//查看之前的交易是否都完成，没有则取消交易
	}
	
	//测试是否可下单
	private void testTrade()
	{
		float tmpprice = 0.5f;//下单价与深度价的差值,使交易可以马上成交
		//价格上涨一个梯度
		if(Math.abs((this.buyOnePrice - this.lastSetpPrice)-tmpprice) > this.priceStep && this.buyOnePrice > this.lastSetpPrice)
		{
			if(this.heaveGood >= this.tradeCount){
				//物品购，可以作出售操作
				sell(this.buyOnePrice - tmpprice);//价格上涨了作出售操作，如售前要先看之前的定单是否有成交,没有则取消
			}
		}else if(Math.abs((this.lastSetpPrice - this.sellOnePrice)-tmpprice) > this.priceStep && this.lastSetpPrice > this.sellOnePrice)
		{//价格下跌,
			float buytmp = this.sellOnePrice + tmpprice;
			if(this.heaveMoney >= this.tradeCount * buytmp){
				//货币够，可以作买入操作
				buy(buytmp);//价格下跌了作出售操作，如售前要先看之前的定单是否有成交,没有则取消
			}
		}
	}
	
	//即时行情数据数组处理
	private void marketDatarefreshtField(FieldMap fieldMap)
	{
		Iterator fieldIterator = fieldMap.iterator();
		String tname = "";
        while (fieldIterator.hasNext()) {
            Field field = (Field) fieldIterator.next();
            if (!isGroupCountField(field)) {
                String value;
				try {
					value = fieldMap.getString(field.getTag());
					//tname
					
					if (dataDict.hasFieldValue(field.getTag())) {
	                    value = dataDict.getValueName(field.getTag(), value);
	                }
					//行情数据
					if(dataDict.getFieldName(field.getTag()).compareTo("MDEntryType") == 0){
						tname = value;
					}else if(dataDict.getFieldName(field.getTag()).compareTo("MDEntryType") == 0){
						
						switch(tname)
						{
						case "BID":		//0.买一价
							this.buyOnePrice = Float.valueOf(value);
							break;
						case "OFFER":	//1.卖一价
							this.sellOnePrice = Float.valueOf(value);
							break;
						case "TRADE":	//2.最新成交价
							float tmpvalue = Float.valueOf(value);
							if (tmpvalue >= this.buyOnePrice && tmpvalue <= this.sellOnePrice){
								this.nowTradePrice = tmpvalue;
							}else{
								this.nowTradePrice = (this.buyOnePrice + this.sellOnePrice)/2.0f;
							}
							break;
						}
					}
				} catch (FieldNotFound e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
            }
        }
        //测试是否达到下单要求
        testTrade();
	}
	//刷新交易数据,买一，卖一，当前成交
	private void DataRefresh(FieldMap fieldMap)
	{
		Iterator groupsKeys = fieldMap.groupKeyIterator();
        while (groupsKeys.hasNext()) {
            int groupCountTag = ((Integer) groupsKeys.next()).intValue();
            Group g = new Group(groupCountTag, 0);
            int i = 1;
            while (fieldMap.hasGroup(i, groupCountTag)) {
                if (i > 1) {
                    System.out.println("  ----");
                }
                try {
					fieldMap.getGroup(i, g);
					marketDatarefreshtField(g);
				} catch (FieldNotFound e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
                i++;
            }
        }
	}
	//已知定单数据更新，如已成交，或部分成交，或取消成功消息
	private void tradeOrderUpdate(FieldMap fieldMap)
	{
		
	}
	//定单编号查询定单
	private void checkOrderBackWithID(FieldMap fieldMap)
	{
		
	}
	//批量定单查询
	private void checkOrdersBack(FieldMap fieldMap)
	{
		
	}
	//交易购买消息反回
	private void tradeBuyOrderBack(FieldMap fieldMap)
	{
		
	}
	//交易出售消息反回
	private void tradeSellOrderBack(FieldMap fieldMap)
	{
		
	}
	//交易取消
	private void cancelOrderBack(FieldMap fieldMap)
	{
		
	}
	//交易执行报告拒绝
	private void tradeExecuteBadBack(FieldMap fieldMap)
	{
		
	}
	//--------------------------------------------------------------------
	//打开市场数据即时更新
	private void openMarketDataUpdate()
	{
		new Thread(new Runnable() {
			@Override
			public void run() {
				quickfix.Message message;
			    try{
			    	//get 1000 latest open orders,批量定单查询
				    message = BTCCMarketDataRequest.myMarketData("BTCCNY");	
				    Session.lookupSession(sessionID).send(message);
				    Thread.sleep(10);
				    System.out.println("thread run .....");
			    } catch (Exception e){
			    	log.info("Exception in trading request: "+e.toString());
			    }
			}
		}).start();
		log.info("请求市场即时数据更新-------"+sessionID);
	}
	
	//请求一次市场行情数据快照
	private void marketOneceTicker()
	{
		new Thread(new Runnable() {
			@Override
			public void run() {
				quickfix.Message message;
			    try{
			    	//get 1000 latest open orders,批量定单查询
				    message = BTCCMarketDataRequest.marketDataFullSnapRequest("BTCCNY");	
				    Session.lookupSession(sessionID).send(message);
				    Thread.sleep(1000);
				    System.out.println("thread run .....");
			    } catch (Exception e){
			    	log.info("Exception in trading request: "+e.toString());
			    }
			}
		}).start();
		
		log.info("请求一次市场行情况据-------"+sessionID);
	}
	
	//取消市场数据即时更新
	private void cancelMarketDataUpdate()
	{
		
		new Thread(new Runnable() {
			@Override
			public void run() {
				//取消市场行情即时更新 (V)
				quickfix.Message message = BTCCMarketDataRequest.unsubscribeIncrementalRequest("BTCCNY");	
				Session.lookupSession(sessionID).send(message);
				try {
					Thread.sleep(3000);
				} catch (InterruptedException e) {
					e.printStackTrace();
				}
			}
		}).start();
		
	}	
	//买单下单
	private boolean buy(float price)
	{
		this.lastSetpPrice = price;
		return true;
	}
	//卖单下单
	private boolean sell(float price)
	{
		this.lastSetpPrice = price;
		return true;
	}
	
	//定单查询,使用已知下单ID查询
	private void orderCheck(String orderID)
	{
		
	}
	
	//定单批量查询,查询count个未成交定单
	private void orderCheckAll()
	{
		new Thread(new Runnable() {
			@Override
			public void run() {
				quickfix.Message message;
				
				String ACCESS_KEY = "";
			    String SECRET_KEY = "";
			    
			    BTCCTradingRequest tradeRequest=new BTCCTradingRequest();
			    try{
			    	//get 1000 latest open orders,批量定单查询
				    message = tradeRequest.createOrderMassStatusRequest(ACCESS_KEY, SECRET_KEY,"BTCCNY");
				    Session.lookupSession(sessionID).send(message);
				    Thread.sleep(10);
				    System.out.println("thread run .....");
			    } catch (Exception e){
			    	log.info("Exception in trading request: "+e.toString());
			    }
			}
		}).start();
		
		log.info("批量定单查询-------"+sessionID);
	}
	
	
	//取消定单
	private void cancelOrder(String orderID)
	{
		
	}
	
	
	//得到服务器数据信息
	public void decodeData(Message message) throws FieldNotFound
	{
		String msgType = message.getHeader().getString(MsgType.FIELD);
		System.out.println("getMsgType:"+msgType);
		switch (msgType) {
		//市场数据请求
        case "X"://市场行情数据即时更新
        	DataRefresh(message);
            //System.out.println("hello");
            break;
        case "V"://取消市场行情即时更新
            System.out.println("hello");
            break;
        case "W":////市场行情数据快照('W'类型)
        	DataRefresh(message);
            System.out.println("hello");
            break;
        case "Y"://市场数据请求拒绝
            System.out.println("hello");
            break;
        //帐户请求
        case "U1001"://帐户信息
            setAccountRes(message);
            //msgPrinter.print(dataDict, message);
            break;
        case "8"://交易定单,指定定单ID查询,批量定单查询,定单取消
        	getServerDataTag8(message);
        	msgPrinter.print(dataDict, message);
        	break;
        default:
        	msgPrinter.print(dataDict, message);
            break;
        }
	}
	//获取交易相关回复
	private void getServerDataTag8(FieldMap fieldMap)
	{
		Iterator fieldIterator = fieldMap.iterator();
		String tname = "";
        while (fieldIterator.hasNext()) {
            Field field = (Field) fieldIterator.next();
            if (!isGroupCountField(field)) {
                String value;
				try {
					value = fieldMap.getString(field.getTag());
					//tname
					
					if (dataDict.hasFieldValue(field.getTag())) {
	                    value = dataDict.getValueName(field.getTag(), value) + " (" + value + ")";
	                }
					//批量查询
					if(dataDict.getFieldName(field.getTag()).compareTo("MassStatusReqID") == 0 && value.compareTo(ReqConfig.reqAllCheckID) == 0){
						checkOrderBackWithID(fieldMap);
						return;
					}
					//交易
					if(dataDict.getFieldName(field.getTag()).compareTo("ClOrdID") == 0){
						switch(value)
						{
						case "10001"://交易购买请求唯一ID
							tradeBuyOrderBack(fieldMap);
							break;
						case "10002"://交易出售请求唯一ID
							tradeSellOrderBack(fieldMap);
							break;
						case "10003"://交易购买市价单请求唯一ID
							tradeBuyOrderBack(fieldMap);
							break;
						case "10004"://交易出售市价单请求唯一ID
							tradeSellOrderBack(fieldMap);
							break;
						case "10005"://已知定单号查询唯一ID
							checkOrderBackWithID(fieldMap);
							break;
						case "10006"://批量查询唯一ID
							break;
						case "10007"://取消订单请求唯一ID
							cancelOrderBack(fieldMap);
							break;
						case "10008"://服务器执行报告拒绝唯一ID
							tradeExecuteBadBack(fieldMap);
							break;
						default:
							msgPrinter.print(dataDict, (quickfix.fix44.Message)fieldMap);
							break;
						}
						
						return;
					}
				} catch (FieldNotFound e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
            }
        }
	}
	    private void printFieldMap(String prefix,String msgType, FieldMap fieldMap)
	            throws FieldNotFound {
	 
	        Iterator fieldIterator = fieldMap.iterator();
	        while (fieldIterator.hasNext()) {
	            Field field = (Field) fieldIterator.next();
	            if (!isGroupCountField(field)) {
	                String value = fieldMap.getString(field.getTag());
	                if (dataDict.hasFieldValue(field.getTag())) {
	                    value = dataDict.getValueName(field.getTag(), fieldMap.getString(field.getTag())) + " (" + value + ")";
	                }
	                System.out.println(prefix + dataDict.getFieldName(field.getTag()) + ": " + value);
	            }
	        }
	 
	        Iterator groupsKeys = fieldMap.groupKeyIterator();
	        while (groupsKeys.hasNext()) {
	            int groupCountTag = ((Integer) groupsKeys.next()).intValue();
	            System.out.println(prefix + dataDict.getFieldName(groupCountTag) + ": count = "
	                    + fieldMap.getInt(groupCountTag));
	            Group g = new Group(groupCountTag, 0);
	            int i = 1;
	            while (fieldMap.hasGroup(i, groupCountTag)) {
	                if (i > 1) {
	                    System.out.println(prefix + "  ----");
	                }
	                fieldMap.getGroup(i, g);
	                printFieldMap(prefix + "  ",msgType, g);
	                i++;
	            }
	        }
	    }
	 
	    private boolean isGroupCountField(Field<?> field) {
	        return dataDict.getFieldTypeEnum(field.getTag()) == FieldType.NumInGroup;
	    }
	
}
