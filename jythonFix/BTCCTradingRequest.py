#!/usr/local/bin/jython
#coding:utf-8

# package com.btcchina.fix;

# //import java.io.IOException;
import java.security.InvalidKeyException as InvalidKeyException
import java.security.NoSuchAlgorithmException as NoSuchAlgorithmException
import java.util.Date as Date

import javax.crypto.Mac as Mac
import javax.crypto.spec.SecretKeySpec as SecretKeySpec
import javax.xml.bind.DatatypeConverter as DatatypeConverter

import quickfix.Message as Message
import quickfix.field.Account as Account
import quickfix.field.ClOrdID as ClOrdID
import quickfix.field.MassStatusReqID as MassStatusReqID
import quickfix.field.MassStatusReqType as MassStatusReqType
import quickfix.field.OrdType as OrdType
import quickfix.field.OrderID as OrderID
import quickfix.field.OrderQty as OrderQty
import quickfix.field.Price as Price
import quickfix.field.Side as Side
import quickfix.field.Symbol as Symbol
import quickfix.field.TransactTime as TransactTime
import quickfix.fix44.NewOrderSingle as NewOrderSingle

import ReqConfig

import AccReqID

class BTCCTradingRequest():
    def __init__(self):
        self.HMAC_SHA1_ALGORITHM = "HmacSHA1"

    # 限价单
    def createNewOrderSingle(self,accesskey,secretkey,side,ordertype,price,amount,symbol):
        methodstr = None
        if side == Side.BUY:
            methodstr = self.toBuyOrder3ParamString(price,amount,symbol)
        elif side == Side.SELL:
            methodstr = self.toSellOrder3ParamString(price, amount, symbol)
        accountString = self.getAccountString(accesskey, secretkey, methodstr)
        newOrderSingleRequest = NewOrderSingle()
        newOrderSingleRequest.set(Account(accountString))
        if side == Side.BUY:
            newOrderSingleRequest.set(ClOrdID(ReqConfig.reqBuyOrderID))
        elif side == Side.SELL:
            newOrderSingleRequest.set(ClOrdID(ReqConfig.reqSellOrderID))
        newOrderSingleRequest.set(OrderQty(amount))
        newOrderSingleRequest.set(OrdType(ordertype))
        # //如果买入 ,OrdType 为1 price 意思为市价单 买30块钱的币  OrderQty无意义
        # //如果买入, OrdType 为2 price 意思 买币单价为30  OrderQty表示购买数量
        # //如果卖出, OrdType 为1 price 无含义,意思为市价卖,OrderQty为卖出数量
        # //如果卖出, OrdType 为2 price 为卖出单价 OrderQty为卖出数量
        newOrderSingleRequest.set(Price(price))
        newOrderSingleRequest.set(Side(side))
        newOrderSingleRequest.set(Symbol(symbol))
        newOrderSingleRequest.set(TransactTime())
        
        print("accountString : " + str(accountString));
        print("methodstr : " + str(methodstr));
        return newOrderSingleRequest

    #市价单
    def createNewOrderSingle(self,accesskey,secretkey,side,ordertype,amount,symbol):
        methodstr = None
        if side == Side.BUY:
            methodstr = self.toBuyOrder3ParamString(None, amount, symbol)
        elif side == Side.SELL:
            methodstr = self.toSellOrder3ParamString(None, amount, symbol)
        accountString = self.getAccountString(accesskey, secretkey, methodstr)
        newOrderSingleRequest = NewOrderSingle()
        newOrderSingleRequest.set(Account(accountString))
        if side == Side.BUY:
            newOrderSingleRequest.set(ClOrdID(ReqConfig.reqBuyOrderMarketID))
        elif side == Side.SELL:
            newOrderSingleRequest.set(ClOrdID(ReqConfig.reqSellOrderMarketID))
        newOrderSingleRequest.set(OrderQty(amount))
        newOrderSingleRequest.set(OrdType(ordertype))
        # //如果买入 ,OrdType 为1 price 意思为市价单 买30块钱的币  OrderQty无意义
        # //如果买入, OrdType 为2 price 意思 买币单价为30  OrderQty表示购买数量
        # //如果卖出, OrdType 为1 price 无含义,意思为市价卖,OrderQty为卖出数量
        # //如果卖出, OrdType 为2 price 为卖出单价 OrderQty为卖出数量
# //        newOrderSingleRequest.set(new Price());
        newOrderSingleRequest.set(Side(side))
        newOrderSingleRequest.set(Symbol(symbol))
        newOrderSingleRequest.set(TransactTime())
    
        print "accountString : " + str(accountString)
        print "methodstr : " + str(methodstr)
        return newOrderSingleRequest
        
    
    # /**
    #  * 取消订单请求
    #  * @throws NoSuchAlgorithmException 
    #  * @throws InvalidKeyException 
    #  */

    def createOrderCancelRequest(self,accesskey,secretkey,orderid,market):
        orderCancelRequest = quickfix.fix44.OrderCancelRequest()
        orderCancelRequest.set(ClOrdID("2"))
        #//orderCancelRequest.set(OrigClOrdID("1231234"))                #必填，但无意义
        orderCancelRequest.set(ClOrdID(ReqConfig.reqCancelOrderID))     #//服务器反回信息标识
        orderCancelRequest.set(Side(Side.SELL))                         #必填，但无意义
        
        methodstr = self.toCancelOrderParamString(orderid, market)
        accountString = self.getAccountString(accesskey, secretkey, methodstr)
        print "accountString : " + str(accountString)
        print "methodstr : " + str(methodstr)
        orderCancelRequest.set(Account(accountString))
        orderCancelRequest.set(Symbol(market))
        orderCancelRequest.set(OrderID(String.valueOf(orderid)))        #订单编号
        orderCancelRequest.set(TransactTime(Date()))
        return orderCancelRequest
    
    # /**
    #  * 订单状态请求
    #  * @throws NoSuchAlgorithmException 
    #  * @throws InvalidKeyException 
    #  */

    def createOrderMassStatusRequest(self,accesskey,secretkey,market):
        orderMassStatusRequest = quickfix.fix44.OrderMassStatusRequest()
        orderMassStatusRequest.set(MassStatusReqID(ReqConfig.reqAllCheckID))
        orderMassStatusRequest.set(MassStatusReqType(MassStatusReqType.STATUS_FOR_ALL_ORDERS))
        orderMassStatusRequest.set(Side(Side.BUY))              #必填，但无意义
        
        methodstr = self.toGetOrdersParamString(market)
        accountString = self.getAccountString(accesskey, secretkey, methodstr)
        orderMassStatusRequest.set(Account(accountString))
        orderMassStatusRequest.set(Symbol("BTCCNY"))
        return orderMassStatusRequest

    #订单号查询定单请求
    def createOrderStatusRequest(self,accesskey,secretkey,market,orderid):
        orderStatusRequest = quickfix.fix44.OrderStatusRequest()
        
        methodstr = self.toGetOrderParamString(orderid, market)
        accountString = self.getAccountString(accesskey, secretkey, methodstr)
        
        orderStatusRequest.set(Account(accountString))
        orderStatusRequest.set(Symbol(market))
        orderStatusRequest.set(OrderID(String.valueOf(orderid)))            #订单编号
        
        orderStatusRequest.set(ClOrdID(ReqConfig.reqOneCheckID))
        orderStatusRequest.set(Side(Side.BUY))                         #必填，但无意义
        return orderStatusRequest

    
    # /**
    #  * 账户信息请求 
    #  * @throws NoSuchAlgorithmException 
    #  * @throws InvalidKeyException 
    #  */
    def createUserAccountRequest(self,accesskey,secretkey):
        accountInfoRequest = com.btcchina.fix.AccountInfoRequest()
        
        methodstr = self.toGetAccountInfoParamString()
        accountString = self.getAccountString(accesskey, secretkey, methodstr)
            
        accountInfoRequest.set(Account(accountString))
        accountInfoRequest.set(AccReqID.AccReqID("123"))
        return accountInfoRequest
        
    def getAccountString(self,accesskey,secretkey,methodstr):
        tonce = "" + str(System.currentTimeMillis() * 1000);    
        params = "tonce=" + str(tonce) + "&accesskey=" + str(accesskey) + "&requestmethod=post&id=1&" + str(methodstr)
    
        hashstr = self.getSignature(params, secretkey)
        userpass = str(accesskey) + ":" + str(hashstr)

        basicAuth = "Basic " + DatatypeConverter.printBase64Binary(bytes(userpass))
    
        return tonce + ":" + basicAuth

    # String getAccountString(String accesskey, String secretkey, String methodstr) throws InvalidKeyException, NoSuchAlgorithmException
    # {   
    #     String tonce = "" + (System.currentTimeMillis() * 1000);    
    #     String params = "tonce=" + tonce.toString() + "&accesskey=" + accesskey + "&requestmethod=post&id=1&" + methodstr;
    
    #     String hash = getSignature(params, secretkey);
    #     String userpass = accesskey + ":" + hash;
    #     String basicAuth = "Basic " + DatatypeConverter.printBase64Binary(userpass.getBytes());
    
    #     return tonce + ":" + basicAuth;         
    # }



    def getSignature(self,data,key):
        #// get an hmac_sha1 key from the raw key bytes
        signingKey = SecretKeySpec(bytes(key), self.HMAC_SHA1_ALGORITHM)

        #// get an hmac_sha1 Mac instance and initialize with the signing key
        mac = Mac.getInstance(self.HMAC_SHA1_ALGORITHM)
        mac.init(signingKey);

        #// compute the hmac on input data bytes
        rawHmac = mac.doFinal(bytes(data))

        return self.bytArrayToHex(rawHmac)
    # String getSignature(String data, String key) throws NoSuchAlgorithmException, InvalidKeyException {

    #     // get an hmac_sha1 key from the raw key bytes
    #     SecretKeySpec signingKey = new SecretKeySpec(key.getBytes(), HMAC_SHA1_ALGORITHM);

    #     // get an hmac_sha1 Mac instance and initialize with the signing key
    #     Mac mac = Mac.getInstance(HMAC_SHA1_ALGORITHM);
    #     mac.init(signingKey);

    #     // compute the hmac on input data bytes
    #     byte[] rawHmac = mac.doFinal(data.getBytes());

    #     return bytArrayToHex(rawHmac);
    # }


    def bytArrayToHex(self,a):
        sb = StringBuilder()
        for b in a:
            tmpstr = "%02x"%(b & 0xff)
            sb.append(tmpstr)
        return str(sb);

    # String bytArrayToHex(byte[] a) {
    #     StringBuilder sb = new StringBuilder();
    #     for (byte b : a)
    #         sb.append(String.format("%02x", b & 0xff));
    #     return sb.toString();
    # }

    def toBuyOrder3ParamString(self,price,amount,market):
        if market:
            market = market.toUpperCase()
        priceString = None
        amountString = None
        if (not market) or market == '' or market == "CNYBTC" or market == "BTCCNY":
        
            market = "BTCCNY";
            if not price or price <= 0:
            
                priceString = "";
            else:
                priceString = "%f"%(price) 
            amountString = "%f"%(amount)
        elif market == "CNYLTC" or market == "LTCCNY":
            market = "LTCCNY";
            if price == None or price <= 0:
            
                priceString = "";
            else:
                priceString = "%f"%price
            
            amountString = "%f"%(amount)

        elif market == "BTCLTC" or market == "LTCBTC":
        
            market = "LTCBTC"
            if not price or price == '':
            
                priceString = ""
            else:
                priceString = "%f"%(price)
            
            amountString = "%f"%(amount)  
        else:
            print "erro toBuyOrder3ParamString"
        
        priceString = self.truncatTailingZeroes(priceString)
        amountString = self.truncatTailingZeroes(amountString)
        return "method=buyOrder3&params=" + priceString + "," + amountString + "," + market

    def toSellOrder3ParamString(self,price,amount,market):
        
        if market:
            market = market.toUpperCase()
        priceString = None
        amountString = None
        if (not market) or market == '' or market == "CNYBTC" or market == "BTCCNY":
        
            market = "BTCCNY";
            if not price or price <= 0:
            
                priceString = "";
            else:
                priceString = "%f"%(price) 
            amountString = "%f"%(amount)
        elif market == "CNYLTC" or market == "LTCCNY":
            market = "LTCCNY";
            if price == None or price <= 0:
            
                priceString = "";
            else:
                priceString = "%f"%price
            
            amountString = "%f"%(amount)

        elif market == "BTCLTC" or market == "LTCBTC":
        
            market = "LTCBTC"
            if not price or price == '':
            
                priceString = ""
            else:
                priceString = "%f"%(price)
            
            amountString = "%f"%(amount)  
        else:
            print "erro toBuyOrder3ParamString"
        
        priceString = self.truncatTailingZeroes(priceString)
        amountString = self.truncatTailingZeroes(amountString)

        return "method=sellOrder3&params=" + priceString + "," + amountString + "," + market;

    def truncatTailingZeroes(self,s):
        #删除最后的.和最后重复的0
        if s[-1] == '.':
            s = s[:-1]
        while s[-1] == '0':
            s = s[:-1]
            pass
        return s
    # String truncatTailingZeroes(String s)
    # {
    #     if(s.indexOf(".") > 0){  
    #         s = s.replaceAll("0+?$", "");//remove redundant 0  
    #         s = s.replaceAll("[.]$", "");//if the last is ., remove  
    #     }  
    #     return s;  
    # }

    def toGetOrderParamString(self,orderid,market):
        retString = "method=getOrder&params=" + str(orderid) + "," + str(market) + ",1"
        return retString

    def toGetOrdersParamString(self,market):
        retString = "method=getOrders&params=1," + str(market) + ",1000,0,0,1"
        return retString

    def toCancelOrderParamString(self,orderid,markey):
        retString = "method=cancelOrder3&params=" + str(orderid) + "," + str(market)
        return retString

    def toGetAccountInfoParamString(self):
        retString = "method=getAccountInfo&params=balance"
        return retString
