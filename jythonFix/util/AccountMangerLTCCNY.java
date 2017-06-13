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
import quickfix.field.OrdType;
import quickfix.field.Side;
import quickfix.fix44.Message;

public class AccountMangerLTCCNY {
	private static final Logger log = Logger.getLogger(AccountMangerTest.class);	//log输出工具
	private DataDictionary dataDict = null;//new DataDictionary("FIX44.xml");	//fix4.4协议
	private MessagePrinter msgPrinter = null;
	public SessionID sessionID = null;		//fix绘话ID
	
	
	private String s_accKey = "";
	private String s_secKey = "";
	
	private boolean isTest = false;
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
	public float nextUpPriceStep = 0.0f;		//下次触发买梯度
	public float nextDownPriceStep = 0.0f;		//下次解发卖梯度
	public int buyCount = 0;				//连续购买次数
	public int sellCount = 0;				//连续出售次数
	
	//帐户初始化
	public float baseMoney = 0.0f;			//起始资金来自帐户数据获取
	public float priceStepBase = 0.0f;			//解发价格梯度黄金分割倍数,基础价格梯度,按黄金分割计算原理来计算,作100级计算，并保存在数组中
	public float priceGoldSteps[];			//100级黄金分割价格梯度
	public float tradeCount = 0.0f;			//单次交易量
	public float tradeOffset = 0.0f;		//作买入和出售下单时的价格与买一和卖一价的偏移，以保证即时成交
	
	//帐户实时更新数据
	public float heaveMoney = 0.0f;			//当前货币量
	public float heaveGood = 0.0f;			//当前物品量
	public float allRes = 0.0f;				//当前总资产数量
	public float nowPrice = 0.0f;			//当前成成交价,当获取到的最新成交价不在买一卖一之内时，最新成交价使用买一价与卖一价的中间值,此值不参与交易运算，只作收益统计
	public float yieldRate = 0.0f;			//收效率=(allRes/baseMoney)*100%

	
	//挂单信息
	private LinkedList<String> orderIDs = new LinkedList<String>(); //已下单，但未完全成交的订单ID
	//市场数据状态
	private boolean isReqMarkDataUpdate = true;		//是否开启市场数据更新
	private boolean isInitAccount = true;
	
	//初始化100级黄金交易梯级数
	private void initGoldSteps()
	{
		float a = 1;
		float b = 1;
		float tmp = 1;
		priceGoldSteps = new float[30];//黄金交易法，最多只到30级价格差，不会再有比这个更大的数据差了
		for(int i = 0;i < 30; i++)
		{
			tmp = a + b;
			priceGoldSteps[i] = b*priceStepBase;
			a = b;
			b = tmp;
			System.out.println("step("+i+")--->"+priceGoldSteps[i]);
		}
	}
	
	/*************************AccountMangerTest********************************/
	public AccountMangerLTCCNY(SessionID pID,float pStepPriceBase,float pTradeCount,float pOffset,String pAccKey,String pSecKey) 
	{
		this.isTest = false;
		System.out.println("priceStep--->"+pStepPriceBase);
		this.priceStepBase = pStepPriceBase;		//初始化价格梯度
        this.tradeCount = pTradeCount;		//初始化单次交易量
        this.sessionID = pID;				//fix绘话ID
        this.tradeOffset = pOffset;			//买一卖一与下单价偏移量
        
        
        s_accKey = pAccKey;
    	s_secKey = pSecKey;
        
        
        initGoldSteps();
        
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
	//初始化
	public AccountMangerLTCCNY(SessionID pID,float pStepPriceBase,float pTradeCount,float pOffset,boolean isTest) {
		
		System.out.println("----------test----------------");
		System.out.println("priceStep--->"+pStepPriceBase);
		this.priceStepBase = pStepPriceBase;		//初始化价格梯度
        this.tradeCount = pTradeCount;		//初始化单次交易量
        this.sessionID = pID;				//fix绘话ID
        this.tradeOffset = pOffset;			//买一卖一与下单价偏移量
        
        initGoldSteps();
        
        this.isTest = true;
       
    }
	/*********************************************************/
	//获取帐户信息
	private void getAccountData()
	{
		new Thread(new Runnable() {
			@Override
			public void run() {
				quickfix.Message message;
				
				String ACCESS_KEY = s_accKey;//"";
			    String SECRET_KEY = s_secKey;//"";
			    
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
	/***************************testLastTradeAdnClanceNotOKTread******************************/
	//查看之前的交易是否都完成，没有则取消交易
	private void testLastTradeAdnClanceNotOKTread()
	{
		//如果这里有未成交定单
		if(orderIDs.size() > 0){
			//在这里取消交易
		}
	}
	
	
	//计算下一个触发价位
	private void testNextPrice()
	{
		
		this.nextUpPriceStep = priceGoldSteps[this.sellCount];
		this.nextDownPriceStep = priceGoldSteps[this.buyCount];
		if(this.isTest)
		{
			//System.out.println("(extUp,sellcount)--->("+this.nextUpPriceStep + "," + this.sellCount +")");
			//System.out.println("(extDown,buyCount)--->("+this.nextDownPriceStep + "," + this.buyCount +")");
		}
	}
	
	private float getTradeBeiShu(float price)
	{
		float tmp = 1.0f;
		for(int i = 0; i < 30;i++)
		{
			if(priceGoldSteps[i] >= price)
			{
				tmp = (i+1.0f)*1.0f;
				break;
			}
		}
		return tmp;
	}
	
	
	//测试
	public void projectTest()
	{
		float[] testprice = new float[500];
		testprice[0] = 4874.6f;
		testprice[1] = 4874.6f;
		testprice[2] = 4874.6f;
		testprice[3] = 4874.6f;
		testprice[4] = 4874.6f;
		testprice[5] = 4874.6f;
		testprice[6] = 4874.6f;
		testprice[7] = 4871.0f;
		testprice[8] = 4870.1f;
		testprice[9] = 4870.0f;
		testprice[10] = 4870.0f;
		testprice[11] = 4870.0f;
		testprice[12] = 4870.0f;
		testprice[13] = 4870.0f;
		testprice[14] = 4864.1f;
		testprice[15] = 4871.5f;
		testprice[16] = 4871.5f;
		testprice[17] = 4872.0f;
		testprice[18] = 4872.1f;
		testprice[19] = 4874.9f;
		testprice[20] = 4874.9f;
		testprice[21] = 4874.9f;
		testprice[22] = 4869.8f;
		testprice[23] = 4871.6f;
		testprice[24] = 4871.9f;
		testprice[25] = 4871.9f;
		testprice[26] = 4871.9f;
		testprice[27] = 4871.9f;
		testprice[28] = 4871.9f;
		testprice[29] = 4871.9f;
		testprice[30] = 4871.7f;
		testprice[31] = 4871.0f;
		testprice[32] = 4868.1f;
		testprice[33] = 4868.0f;
		testprice[34] = 4871.7f;
		testprice[35] = 4871.7f;
		testprice[36] = 4871.7f;
		testprice[37] = 4871.7f;
		testprice[38] = 4871.7f;
		testprice[39] = 4871.7f;
		testprice[40] = 4871.7f;
		testprice[41] = 4871.7f;
		testprice[42] = 4870.1f;
		testprice[43] = 4870.1f;
		testprice[44] = 4870.1f;
		testprice[45] = 4870.1f;
		testprice[46] = 4872.0f;
		testprice[47] = 4872.0f;
		testprice[48] = 4872.0f;
		testprice[49] = 4872.4f;
		testprice[50] = 4878.3f;
		testprice[51] = 4881.0f;
		testprice[52] = 4882.7f;
		testprice[53] = 4882.7f;
		testprice[54] = 4882.9f;
		testprice[55] = 4883.0f;
		testprice[56] = 4883.0f;
		testprice[57] = 4884.0f;
		testprice[58] = 4884.0f;
		testprice[59] = 4884.0f;
		testprice[60] = 4884.0f;
		testprice[61] = 4887.1f;
		testprice[62] = 4887.0f;
		testprice[63] = 4887.0f;
		testprice[64] = 4887.0f;
		testprice[65] = 4887.0f;
		testprice[66] = 4887.0f;
		testprice[67] = 4888.0f;
		testprice[68] = 4888.9f;
		testprice[69] = 4888.0f;
		testprice[70] = 4885.9f;
		testprice[71] = 4885.9f;
		testprice[72] = 4885.9f;
		testprice[73] = 4885.9f;
		testprice[74] = 4885.9f;
		testprice[75] = 4885.9f;
		testprice[76] = 4885.9f;
		testprice[77] = 4885.9f;
		testprice[78] = 4885.9f;
		testprice[79] = 4885.9f;
		testprice[80] = 4882.0f;
		testprice[81] = 4881.2f;
		testprice[82] = 4881.2f;
		testprice[83] = 4880.9f;
		testprice[84] = 4880.8f;
		testprice[85] = 4880.8f;
		testprice[86] = 4880.8f;
		testprice[87] = 4873.0f;
		testprice[88] = 4874.5f;
		testprice[89] = 4874.5f;
		testprice[90] = 4878.6f;
		testprice[91] = 4880.7f;
		testprice[92] = 4880.7f;
		testprice[93] = 4880.7f;
		testprice[94] = 4885.0f;
		testprice[95] = 4885.0f;
		testprice[96] = 4885.0f;
		testprice[97] = 4888.0f;
		testprice[98] = 4890.0f;
		testprice[99] = 4890.0f;
		testprice[100] = 4895.0f;
		testprice[101] = 4895.0f;
		testprice[102] = 4895.0f;
		testprice[103] = 4895.0f;
		testprice[104] = 4895.0f;
		testprice[105] = 4895.0f;
		testprice[106] = 4895.0f;
		testprice[107] = 4896.0f;
		testprice[108] = 4896.9f;
		testprice[109] = 4896.9f;
		testprice[110] = 4896.9f;
		testprice[111] = 4896.9f;
		testprice[112] = 4896.9f;
		testprice[113] = 4896.9f;
		testprice[114] = 4896.9f;
		testprice[115] = 4896.0f;
		testprice[116] = 4896.0f;
		testprice[117] = 4896.0f;
		testprice[118] = 4896.0f;
		testprice[119] = 4897.0f;
		testprice[120] = 4899.0f;
		testprice[121] = 4899.0f;
		testprice[122] = 4899.0f;
		testprice[123] = 4900.0f;
		testprice[124] = 4900.0f;
		testprice[125] = 4900.0f;
		testprice[126] = 4900.0f;
		testprice[127] = 4900.0f;
		testprice[128] = 4900.0f;
		testprice[129] = 4900.0f;
		testprice[130] = 4900.0f;
		testprice[131] = 4902.1f;
		testprice[132] = 4902.1f;
		testprice[133] = 4902.1f;
		testprice[134] = 4902.1f;
		testprice[135] = 4902.1f;
		testprice[136] = 4902.1f;
		testprice[137] = 4902.1f;
		testprice[138] = 4900.1f;
		testprice[139] = 4900.1f;
		testprice[140] = 4900.1f;
		testprice[141] = 4900.1f;
		testprice[142] = 4900.1f;
		testprice[143] = 4900.1f;
		testprice[144] = 4900.1f;
		testprice[145] = 4900.1f;
		testprice[146] = 4900.1f;
		testprice[147] = 4900.0f;
		testprice[148] = 4900.1f;
		testprice[149] = 4900.1f;
		testprice[150] = 4900.1f;
		testprice[151] = 4900.1f;
		testprice[152] = 4900.1f;
		testprice[153] = 4900.1f;
		testprice[154] = 4900.1f;
		testprice[155] = 4900.1f;
		testprice[156] = 4900.1f;
		testprice[157] = 4900.1f;
		testprice[158] = 4900.1f;
		testprice[159] = 4900.1f;
		testprice[160] = 4900.1f;
		testprice[161] = 4900.1f;
		testprice[162] = 4900.1f;
		testprice[163] = 4900.1f;
		testprice[164] = 4900.1f;
		testprice[165] = 4900.1f;
		testprice[166] = 4900.1f;
		testprice[167] = 4900.0f;
		testprice[168] = 4900.0f;
		testprice[169] = 4897.1f;
		testprice[170] = 4895.9f;
		testprice[171] = 4895.9f;
		testprice[172] = 4895.9f;
		testprice[173] = 4895.9f;
		testprice[174] = 4895.9f;
		testprice[175] = 4895.9f;
		testprice[176] = 4895.9f;
		testprice[177] = 4895.9f;
		testprice[178] = 4895.9f;
		testprice[179] = 4895.9f;
		testprice[180] = 4895.9f;
		testprice[181] = 4895.9f;
		testprice[182] = 4895.9f;
		testprice[183] = 4895.0f;
		testprice[184] = 4895.0f;
		testprice[185] = 4895.0f;
		testprice[186] = 4892.1f;
		testprice[187] = 4892.0f;
		testprice[188] = 4880.0f;
		testprice[189] = 4880.0f;
		testprice[190] = 4873.3f;
		testprice[191] = 4873.3f;
		testprice[192] = 4873.1f;
		testprice[193] = 4873.1f;
		testprice[194] = 4872.2f;
		testprice[195] = 4872.2f;
		testprice[196] = 4872.2f;
		testprice[197] = 4871.9f;
		testprice[198] = 4871.9f;
		testprice[199] = 4871.9f;
		testprice[200] = 4871.9f;
		testprice[201] = 4871.9f;
		testprice[202] = 4871.9f;
		testprice[203] = 4871.9f;
		testprice[204] = 4871.9f;
		testprice[205] = 4871.8f;
		testprice[206] = 4871.8f;
		testprice[207] = 4871.0f;
		testprice[208] = 4871.0f;
		testprice[209] = 4871.0f;
		testprice[210] = 4871.0f;
		testprice[211] = 4871.0f;
		testprice[212] = 4870.0f;
		testprice[213] = 4868.0f;
		testprice[214] = 4860.3f;
		testprice[215] = 4860.3f;
		testprice[216] = 4860.0f;
		testprice[217] = 4858.0f;
		testprice[218] = 4855.0f;
		testprice[219] = 4853.0f;
		testprice[220] = 4850.0f;
		testprice[221] = 4850.0f;
		testprice[222] = 4845.0f;
		testprice[223] = 4842.0f;
		testprice[224] = 4842.0f;
		testprice[225] = 4842.0f;
		testprice[226] = 4841.3f;
		testprice[227] = 4841.2f;
		testprice[228] = 4844.3f;
		testprice[229] = 4844.3f;
		testprice[230] = 4844.3f;
		testprice[231] = 4844.3f;
		testprice[232] = 4844.3f;
		testprice[233] = 4844.3f;
		testprice[234] = 4844.3f;
		testprice[235] = 4844.3f;
		testprice[236] = 4844.3f;
		testprice[237] = 4854.9f;
		testprice[238] = 4854.9f;
		testprice[239] = 4854.9f;
		testprice[240] = 4854.9f;
		testprice[241] = 4854.9f;
		testprice[242] = 4854.9f;
		testprice[243] = 4854.9f;
		testprice[244] = 4854.9f;
		testprice[245] = 4854.9f;
		testprice[246] = 4854.9f;
		testprice[247] = 4854.9f;
		testprice[248] = 4854.9f;
		testprice[249] = 4854.9f;
		testprice[250] = 4854.9f;
		testprice[251] = 4854.9f;
		testprice[252] = 4854.9f;
		testprice[253] = 4854.9f;
		testprice[254] = 4854.9f;
		testprice[255] = 4854.9f;
		testprice[256] = 4850.0f;
		testprice[257] = 4850.1f;
		testprice[258] = 4854.9f;
		testprice[259] = 4854.9f;
		testprice[260] = 4854.9f;
		testprice[261] = 4851.4f;
		testprice[262] = 4852.0f;
		testprice[263] = 4854.9f;
		testprice[264] = 4854.9f;
		testprice[265] = 4854.9f;
		testprice[266] = 4852.1f;
		testprice[267] = 4854.0f;
		testprice[268] = 4854.0f;
		testprice[269] = 4854.0f;
		testprice[270] = 4854.0f;
		testprice[271] = 4852.1f;
		testprice[272] = 4852.0f;
		testprice[273] = 4852.0f;
		testprice[274] = 4852.0f;
		testprice[275] = 4852.0f;
		testprice[276] = 4852.0f;
		testprice[277] = 4852.0f;
		testprice[278] = 4852.0f;
		testprice[279] = 4851.0f;
		testprice[280] = 4851.0f;
		testprice[281] = 4851.0f;
		testprice[282] = 4851.0f;
		testprice[283] = 4851.0f;
		testprice[284] = 4851.0f;
		testprice[285] = 4851.0f;
		testprice[286] = 4851.0f;
		testprice[287] = 4850.0f;
		testprice[288] = 4849.0f;
		testprice[289] = 4848.8f;
		testprice[290] = 4848.0f;
		testprice[291] = 4848.0f;
		testprice[292] = 4848.0f;
		testprice[293] = 4844.5f;
		testprice[294] = 4844.0f;
		testprice[295] = 4843.0f;
		testprice[296] = 4843.0f;
		testprice[297] = 4843.0f;
		testprice[298] = 4841.2f;
		testprice[299] = 4841.0f;
		testprice[300] = 4841.0f;
		testprice[301] = 4840.1f;
		testprice[302] = 4840.0f;
		testprice[303] = 4840.0f;
		testprice[304] = 4840.0f;
		testprice[305] = 4836.0f;
		testprice[306] = 4835.0f;
		testprice[307] = 4833.0f;
		testprice[308] = 4830.6f;
		testprice[309] = 4830.0f;
		testprice[310] = 4830.0f;
		testprice[311] = 4830.0f;
		testprice[312] = 4830.0f;
		testprice[313] = 4830.0f;
		testprice[314] = 4830.0f;
		testprice[315] = 4825.0f;
		testprice[316] = 4825.0f;
		testprice[317] = 4825.0f;
		testprice[318] = 4825.0f;
		testprice[319] = 4825.0f;
		testprice[320] = 4825.0f;
		testprice[321] = 4825.0f;
		testprice[322] = 4825.0f;
		testprice[323] = 4821.0f;
		testprice[324] = 4821.0f;
		testprice[325] = 4820.0f;
		testprice[326] = 4820.0f;
		testprice[327] = 4820.0f;
		testprice[328] = 4820.0f;
		testprice[329] = 4816.5f;
		testprice[330] = 4815.0f;
		testprice[331] = 4815.1f;
		testprice[332] = 4815.6f;
		testprice[333] = 4815.6f;
		testprice[334] = 4815.6f;
		testprice[335] = 4815.6f;
		testprice[336] = 4815.6f;
		testprice[337] = 4815.3f;
		testprice[338] = 4815.1f;
		testprice[339] = 4815.1f;
		testprice[340] = 4815.0f;
		testprice[341] = 4815.0f;
		testprice[342] = 4815.0f;
		testprice[343] = 4815.0f;
		testprice[344] = 4815.0f;
		testprice[345] = 4810.0f;
		testprice[346] = 4810.0f;
		testprice[347] = 4810.0f;
		testprice[348] = 4805.0f;
		testprice[349] = 4801.0f;
		testprice[350] = 4801.0f;
		testprice[351] = 4801.0f;
		testprice[352] = 4801.0f;
		testprice[353] = 4800.0f;
		testprice[354] = 4800.0f;
		testprice[355] = 4800.0f;
		testprice[356] = 4800.0f;
		testprice[357] = 4800.0f;
		testprice[358] = 4797.0f;
		testprice[359] = 4790.1f;
		testprice[360] = 4790.0f;
		testprice[361] = 4780.1f;
		testprice[362] = 4780.1f;
		testprice[363] = 4780.1f;
		testprice[364] = 4780.1f;
		testprice[365] = 4780.0f;
		testprice[366] = 4807.4f;
		testprice[367] = 4807.4f;
		testprice[368] = 4807.4f;
		testprice[369] = 4807.3f;
		testprice[370] = 4790.1f;
		testprice[371] = 4780.0f;
		testprice[372] = 4780.0f;
		testprice[373] = 4780.0f;
		testprice[374] = 4780.0f;
		testprice[375] = 4775.0f;
		testprice[376] = 4771.0f;
		testprice[377] = 4770.0f;
		testprice[378] = 4770.0f;
		testprice[379] = 4766.0f;
		testprice[380] = 4766.0f;
		testprice[381] = 4815.0f;
		testprice[382] = 4780.1f;
		testprice[383] = 4800.0f;
		testprice[384] = 4766.0f;
		testprice[385] = 4765.0f;
		testprice[386] = 4760.0f;
		testprice[387] = 4760.0f;
		testprice[388] = 4760.0f;
		testprice[389] = 4762.0f;
		testprice[390] = 4762.0f;
		testprice[391] = 4760.0f;
		testprice[392] = 4760.0f;
		testprice[393] = 4760.0f;
		testprice[394] = 4760.0f;
		testprice[395] = 4770.0f;
		testprice[396] = 4762.0f;
		testprice[397] = 4760.0f;
		testprice[398] = 4760.0f;
		testprice[399] = 4762.2f;
		testprice[400] = 4760.0f;
		testprice[401] = 4756.0f;
		testprice[402] = 4755.0f;
		testprice[403] = 4755.0f;
		testprice[404] = 4755.0f;
		testprice[405] = 4754.2f;
		testprice[406] = 4752.0f;
		testprice[407] = 4751.0f;
		testprice[408] = 4751.0f;
		testprice[409] = 4750.1f;
		testprice[410] = 4750.0f;
		testprice[411] = 4750.0f;
		testprice[412] = 4750.0f;
		testprice[413] = 4750.0f;
		testprice[414] = 4760.0f;
		testprice[415] = 4751.3f;
		testprice[416] = 4750.5f;
		testprice[417] = 4750.1f;
		testprice[418] = 4750.1f;
		testprice[419] = 4750.0f;
		testprice[420] = 4750.0f;
		testprice[421] = 4750.0f;
		testprice[422] = 4750.0f;
		testprice[423] = 4750.0f;
		testprice[424] = 4800.0f;
		testprice[425] = 4800.0f;
		testprice[426] = 4800.0f;
		testprice[427] = 4815.0f;
		testprice[428] = 4815.0f;
		testprice[429] = 4790.0f;
		testprice[430] = 4760.0f;
		testprice[431] = 4772.2f;
		testprice[432] = 4772.1f;
		testprice[433] = 4772.0f;
		testprice[434] = 4766.0f;
		testprice[435] = 4772.2f;
		testprice[436] = 4772.2f;
		testprice[437] = 4772.6f;
		testprice[438] = 4772.6f;
		testprice[439] = 4772.6f;
		testprice[440] = 4772.6f;
		testprice[441] = 4772.6f;
		testprice[442] = 4773.0f;
		testprice[443] = 4773.1f;
		testprice[444] = 4773.0f;
		testprice[445] = 4773.0f;
		testprice[446] = 4773.0f;
		testprice[447] = 4775.0f;
		testprice[448] = 4778.0f;
		testprice[449] = 4776.6f;
		testprice[450] = 4778.0f;
		testprice[451] = 4776.6f;
		testprice[452] = 4776.6f;
		testprice[453] = 4776.6f;
		testprice[454] = 4776.6f;
		testprice[455] = 4775.0f;
		testprice[456] = 4775.0f;
		testprice[457] = 4773.0f;
		testprice[458] = 4772.6f;
		testprice[459] = 4772.6f;
		testprice[460] = 4779.0f;
		testprice[461] = 4779.0f;
		testprice[462] = 4772.6f;
		testprice[463] = 4773.0f;
		testprice[464] = 4772.6f;
		testprice[465] = 4773.0f;
		testprice[466] = 4778.0f;
		testprice[467] = 4778.0f;
		testprice[468] = 4772.7f;
		testprice[469] = 4772.7f;
		testprice[470] = 4772.7f;
		testprice[471] = 4772.6f;
		testprice[472] = 4772.6f;
		testprice[473] = 4772.6f;
		testprice[474] = 4772.0f;
		testprice[475] = 4779.8f;
		testprice[476] = 4778.0f;
		testprice[477] = 4772.0f;
		testprice[478] = 4770.0f;
		testprice[479] = 4770.0f;
		testprice[480] = 4778.0f;
		testprice[481] = 4778.0f;
		testprice[482] = 4778.0f;
		testprice[483] = 4778.0f;
		testprice[484] = 4777.0f;
		testprice[485] = 4777.0f;
		testprice[486] = 4777.0f;
		testprice[487] = 4770.0f;
		testprice[488] = 4779.0f;
		testprice[489] = 4770.0f;
		testprice[490] = 4766.0f;
		testprice[491] = 4779.8f;
		testprice[492] = 4779.0f;
		testprice[493] = 4766.0f;
		testprice[494] = 4766.0f;
		testprice[495] = 4763.0f;
		testprice[496] = 4763.0f;
		testprice[497] = 4777.0f;
		testprice[498] = 4763.0f;
		testprice[499] = 4763.0f;
		
		this.lastSetpPrice = testprice[0];
		
		for(int i = 0;i<500;i++)
		{
			this.buyOnePrice = this.sellOnePrice = testprice[i];
			testTrade();
		}
		
	}
	
	
	//测试是否可下单
	private void testTrade()
	{
		float tmpprice = this.tradeOffset;//下单价与深度价的差值,使交易可以马上成交
		if(this.lastSetpPrice == 0.0)
		{
			if(nowTradePrice == 0.0)
			{
				return;
			}
			this.lastSetpPrice = nowTradePrice;
			if(this.buyOnePrice == 0.0 || this.sellOnePrice == 0.0)
			{
				return;
			}
		}
		//Thread.currentThread()
		
		//Thread.currentThread().getId();
		//System.out.println("test:buy-sellOnePrice("+this.buyOnePrice+"-"+this.sellOnePrice+"),lastSetPrice("+this.lastSetpPrice+"),"+"priceStep("+this.priceStep+")");
		//价格上涨一个梯度
		
		testNextPrice();
		//价格上涨了一个下一个要求的上涨梯度
		if(this.buyOnePrice > this.lastSetpPrice && Math.abs((this.buyOnePrice - this.lastSetpPrice)-tmpprice) > this.nextUpPriceStep)
		{
			//计算价格差值
			float chazhi = Math.abs((this.buyOnePrice - this.lastSetpPrice)-tmpprice) - this.nextUpPriceStep;
			float counttmp = getTradeBeiShu(chazhi);
			
			//物品购，可以作出售操作
			float selltmp = this.buyOnePrice - tmpprice;
			//System.out.println("chazhi=" + chazhi + ",counttmp=" + counttmp + ",sellprice=" + selltmp);
			sell(selltmp,counttmp);//价格上涨了作出售操作，如售前要先看之前的定单是否有成交,没有则取消

		}else if(this.lastSetpPrice > this.sellOnePrice && Math.abs((this.lastSetpPrice - this.sellOnePrice)-tmpprice) > this.nextDownPriceStep)
		{//价格下跌,
			float buytmp = this.sellOnePrice + tmpprice;

			//货币够，可以作买入操作
			float chazhi = Math.abs((this.lastSetpPrice - this.sellOnePrice)-tmpprice) - this.nextDownPriceStep;
			float counttmp = getTradeBeiShu(chazhi);
			//System.out.println("chazhi=" + chazhi + ",counttmp=" + counttmp + ",buyprice=" + buytmp);
			buy(buytmp,counttmp);//价格下跌了作出售操作，如售前要先看之前的定单是否有成交,没有则取消

		}
	}
	
	/**************************openMarketDataUpdate*******************************/
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
					}else if(dataDict.getFieldName(field.getTag()).compareTo("MDEntryPx") == 0){
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
        //System.out.println("price:"+this.nowTradePrice);
        //测试是否达到下单要求
        testTrade();
	}
	//刷新交易数据,买一，卖一，当前成交
	private void DataRefresh(FieldMap fieldMap)
	{
//		try {
//			msgPrinter.print(dataDict, (quickfix.fix44.Message)fieldMap);
//		} catch (FieldNotFound e1) {
//			// TODO Auto-generated catch block
//			e1.printStackTrace();
//		}
		Iterator groupsKeys = fieldMap.groupKeyIterator();
        while (groupsKeys.hasNext()) {
            int groupCountTag = ((Integer) groupsKeys.next()).intValue();
            Group g = new Group(groupCountTag, 0);
            int i = 1;
            while (fieldMap.hasGroup(i, groupCountTag)) {
                if (i > 1) {
                    //System.out.println("  ----");
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
	
	
	/**************************checkOrderBackWithID*******************************/
	//定单编号查询定单
	private void checkOrderBackWithID(FieldMap fieldMap)
	{
		
	}
	
	//定单查询,使用已知下单ID查询
	private void orderCheck(String orderID)
	{
		
	}
	
	/*************************orderCheckAll********************************/
	//定单批量查询,查询count个未成交定单
	private void orderCheckAll()
	{
		new Thread(new Runnable() {
			@Override
			public void run() {
				quickfix.Message message;
				
				String ACCESS_KEY = s_accKey;//"";
			    String SECRET_KEY = s_secKey;//"";
			    
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
	//批量定单查询
	private void checkOrdersBack(FieldMap fieldMap)
	{
		//批量定单查询结果处理
		//.....
		//统计完之后，如果当前是初始化系统，则取消所有未完成交易
		if(isInitAccount){
			testLastTradeAdnClanceNotOKTread();
		}
	}
	/************************buy*********************************/
	//买单下单
	//单次购买最小量的一定倍数
	private boolean buy(final float price,final float count)
	{
		if(Math.abs(price - this.lastSetpPrice) < priceGoldSteps[0]){
			System.out.println("buy so step small---->(price,laststepprice)=>("+ price + "," + this.lastSetpPrice + "),count=" + count);
			return false;
		}
		this.lastSetpPrice = price;
		if(this.sellCount > 0)
		{
			this.sellCount = 0;
			this.buyCount = 1;
		}else{
			this.buyCount += 1;
		}
		
		if(this.isTest)
		{
			System.out.println("test buy price---->"+price);
			return false;
		}
		new Thread(new Runnable() {
			@Override
			public void run() {
				String ACCESS_KEY = s_accKey;//"";
			    String SECRET_KEY = s_secKey;//"";
				quickfix.Message message;
				
			    try{
			    	//get 1000 latest open orders,批量定单查询
			    	BTCCTradingRequest tradeRequest=new BTCCTradingRequest();
					message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.BUY, OrdType.LIMIT, price, (tradeCount*count), "BTCCNY"); //
				    Session.lookupSession(sessionID).send(message);
				    Thread.sleep(10);
				    System.out.println("run buy--->"+price + ",count-->" + count);
			    } catch (Exception e){
			    	log.info("Exception in trading buy: "+e.toString());
			    }
			}
		}).start();
		
		
		
		return true;
	}
	//单次购买一个最小量
	private boolean buy(final float price)
	{
		this.lastSetpPrice = price;
		if(this.sellCount > 0)
		{
			this.sellCount = 0;
			this.buyCount = 1;
		}else{
			this.buyCount += 1;
		}
		
		if(this.isTest)
		{
			System.out.println("test buy price---->"+price);
			return false;
		}
		new Thread(new Runnable() {
			@Override
			public void run() {
				String ACCESS_KEY = s_accKey;//"";
			    String SECRET_KEY = s_secKey;//"";
				quickfix.Message message;
				
			    try{
			    	//get 1000 latest open orders,批量定单查询
			    	BTCCTradingRequest tradeRequest=new BTCCTradingRequest();
					message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.BUY, OrdType.LIMIT, price, tradeCount, "BTCCNY"); //
				    Session.lookupSession(sessionID).send(message);
				    Thread.sleep(10);
				    System.out.println("run buy--->"+ price);
			    } catch (Exception e){
			    	log.info("Exception in trading buy: "+e.toString());
			    }
			}
		}).start();
		
		
		
		return true;
	}
	//交易购买消息反回
	private void tradeBuyOrderBack(FieldMap fieldMap)
	{
		System.out.println("buy order back");
	}
	/************************sell*********************************/
	//卖单下单
	//因为交易连接断开过，价格差别比较大，要设置下单倍数,
	private boolean sell(final float price,final float count)
	{
		if(Math.abs(price - this.lastSetpPrice) < priceGoldSteps[0]){
			System.out.println("sell so step small---->(price,laststepprice)=>("+ price + "," + this.lastSetpPrice + "),count=" + count);
			return false;
		}
		this.lastSetpPrice = price;
		if(this.buyCount > 0)
		{
			this.buyCount = 0;
			this.sellCount = 1;
		}else{
			this.sellCount += 1;
		}
		if(this.isTest)
		{
			System.out.println("test sell price---->"+price);
			return false;
		}
		new Thread(new Runnable() {
			@Override
			public void run() {
				String ACCESS_KEY = s_accKey;//"";
			    String SECRET_KEY = s_secKey;//"";
				quickfix.Message message;
				
			    try{
			    	//get 1000 latest open orders,批量定单查询
			    	BTCCTradingRequest tradeRequest=new BTCCTradingRequest();
					message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.SELL, OrdType.LIMIT, price, (tradeCount*count), "BTCCNY"); //
				    Session.lookupSession(sessionID).send(message);
				    Thread.sleep(10);
				    System.out.println("run sell--->"+price + ",count-->" + count);
			    } catch (Exception e){
			    	log.info("Exception in trading sell: "+e.toString());
			    }
			}
		}).start();
		
		
		return true;
	}
	//以默认最小成交量下单
	private boolean sell(final float price)
	{
		this.lastSetpPrice = price;
		if(this.buyCount > 0)
		{
			this.buyCount = 0;
			this.sellCount = 1;
		}else{
			this.sellCount += 1;
		}
		if(this.isTest)
		{
			System.out.println("test sell price---->"+price);
			return false;
		}
		new Thread(new Runnable() {
			@Override
			public void run() {
				String ACCESS_KEY = s_accKey;//"";
			    String SECRET_KEY = s_secKey;//"";
				quickfix.Message message;
				
			    try{
			    	//get 1000 latest open orders,批量定单查询
			    	BTCCTradingRequest tradeRequest=new BTCCTradingRequest();
					message = tradeRequest.createNewOrderSingle(ACCESS_KEY, SECRET_KEY, Side.SELL, OrdType.LIMIT, price, tradeCount, "BTCCNY"); //
				    Session.lookupSession(sessionID).send(message);
				    Thread.sleep(10);
				    System.out.println("run sell--->"+price);
			    } catch (Exception e){
			    	log.info("Exception in trading sell: "+e.toString());
			    }
			}
		}).start();
		
		
		return true;
	}
	//交易出售消息反回
	private void tradeSellOrderBack(FieldMap fieldMap)
	{
		System.out.println("sell order back");
	}
	/************************cancelOrder*********************************/
	//取消定单
	private void cancelOrder(String orderID)
	{
		
	}
	//交易取消
	private void cancelOrderBack(FieldMap fieldMap)
	{
		
	}
	/************************tradeExecuteBadBack*********************************/
	
	//交易执行报告拒绝
	private void tradeExecuteBadBack(FieldMap fieldMap)
	{
		
	}
	//--------------------------------------------------------------------
	/************************marketOneceTicker*********************************/
	
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


	

	

	
	

	
	
	//得到服务器数据信息
	public void decodeData(Message message) throws FieldNotFound
	{
		String msgType = message.getHeader().getString(MsgType.FIELD);
//		System.out.println("getMsgType:"+msgType);
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
            break;
        case "Y"://市场数据请求拒绝
            System.out.println("market erro request");
            break;
        //帐户请求
        case "U1001"://帐户信息
            setAccountRes(message);
            //msgPrinter.print(dataDict, message);
            break;
        case "8"://交易定单,指定定单ID查询,批量定单查询,定单取消
        	getServerDataTag8(message);
        	//msgPrinter.print(dataDict, message);
        	break;
        default:
        	System.out.println("print default message");
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
						checkOrdersBack(fieldMap);
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
							System.out.println("print default message for trade");
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
