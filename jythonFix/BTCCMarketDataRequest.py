#!/usr/local/bin/jython
#coding:utf-8

import quickfix.Message as Message
import quickfix.field.MDEntryType as MDEntryType
import quickfix.field.NoMDEntryTypes as NoMDEntryTypes
import quickfix.field.MDReqID as MDReqID
import quickfix.field.MarketDepth as MarketDepth
import quickfix.field.SubscriptionRequestType as SubscriptionRequestType
import quickfix.field.Symbol as Symbol

import quickfix.fix44.MarketDataRequest as MarketDataRequest
# /**
#  * MarkertData Request
#  * @author BTCChina
#  */
class BTCCMarketDataRequest():
    def __init__(self):
        pass
    
    def marketDataFullSnapRequest(self,symbol):
        tickerRequest = MarketDataRequest()
        
        noRelatedSym = MarketDataRequest.NoRelatedSym()
        noRelatedSym.set(Symbol(symbol))
        tickerRequest.addGroup(noRelatedSym)
                
        tickerRequest.set(MDReqID("123"))
        tickerRequest.set(SubscriptionRequestType('0'))
        tickerRequest.set(MarketDepth(0))
        
        self.addMDType(tickerRequest, '0')
        self.addMDType(tickerRequest, '1')
        self.addMDType(tickerRequest, '2')
        self.addMDType(tickerRequest, '3')
        self.addMDType(tickerRequest, '4')
        self.addMDType(tickerRequest, '5')
        self.addMDType(tickerRequest, '6')
        self.addMDType(tickerRequest, '7')
        self.addMDType(tickerRequest, '8')
        self.addMDType(tickerRequest, '9')
        self.addMDType(tickerRequest, 'A')
        self.addMDType(tickerRequest, 'B')
        self.addMDType(tickerRequest, 'C')
            
        return tickerRequest

    
    # /**
    #  * 市场数据即时更新 (V)
    #  * @return @tickerRequest request message
    #  */
    def myMarketData(self,symbol): 
        tickerRequest = MarketDataRequest()
        
        noRelatedSym = MarketDataRequest.NoRelatedSym()
        noRelatedSym.set(Symbol(symbol))
        tickerRequest.addGroup(noRelatedSym)
                
        tickerRequest.set(MDReqID("123"))   
        tickerRequest.set(SubscriptionRequestType('1'))
        tickerRequest.set(MarketDepth(0))
        
        self.addMDType(tickerRequest, '0')
        self.addMDType(tickerRequest, '1')
        self.addMDType(tickerRequest, '2')
#       self.addMDType(tickerRequest, '3');
#       self.addMDType(tickerRequest, '4');
#       self.addMDType(tickerRequest, '5');
#       self.addMDType(tickerRequest, '6');
#       self.addMDType(tickerRequest, '7');
#       self.addMDType(tickerRequest, '8');
#       self.addMDType(tickerRequest, '9');
#       self.addMDType(tickerRequest, 'A');
#       self.addMDType(tickerRequest, 'B');
#       self.addMDType(tickerRequest, 'C');
            
        return tickerRequest
    
    
    # /**
    #  * MARKET DATA INCREMENTAL REFRESH REQUEST (V)
    #  * @return @tickerRequest request message
    # 市场行情即时更新--Market Data Incremental Refresh
# 当用户订阅了市场行情即时更新('X'类型)消息以后，每当市场行情数据发生变动时，
# 服务端就会立即推送相应的市场行情数据给客户端。 
# 目前有8种行情数据可以通过MDEntryType(标签269)返回给用户，
# 包含买一(0), 卖一(1), 最新成交价(2), 昨日收盘价(5), 
# 24小时内最高成交价(7), 24小时内最低成交价(8), 24小时内平均成交价(9) 和 24小时内成交量(B).
# 在市场行情即时更新响应中有更加详尽的描述。
    #  */
    def marketDataIncrementalRequest(self, symbol):
        tickerRequest = MarketDataRequest()
        
        noRelatedSym = MarketDataRequest.NoRelatedSym()
        noRelatedSym.set(Symbol(symbol))
        tickerRequest.addGroup(noRelatedSym)
                
        tickerRequest.set(MDReqID("123"))   
        tickerRequest.set(SubscriptionRequestType('1'))
        tickerRequest.set(MarketDepth(0))
        
        self.addMDType(tickerRequest, '0')
        self.addMDType(tickerRequest, '1')
        self.addMDType(tickerRequest, '2')
        self.addMDType(tickerRequest, '3')
        self.addMDType(tickerRequest, '4')
        self.addMDType(tickerRequest, '5')
        self.addMDType(tickerRequest, '6')
        self.addMDType(tickerRequest, '7')
        self.addMDType(tickerRequest, '8')
        self.addMDType(tickerRequest, '9')
        self.addMDType(tickerRequest, 'A')
        self.addMDType(tickerRequest, 'B')
        self.addMDType(tickerRequest, 'C')
            
        return tickerRequest
    
    # /**
    #  * UNSUBSCRIBE MARKET DATA INCREMENTAL REFRESH (V)
    #  * @return @tickerRequest request message
    #  */
    def unsubscribeIncrementalRequest(self,symbol):
        tickerRequest = MarketDataRequest()
        
        noRelatedSym = MarketDataRequest.NoRelatedSym()
        noRelatedSym.set(Symbol(symbol))
        tickerRequest.addGroup(noRelatedSym)
                
        tickerRequest.set(MDReqID("123"))   
        tickerRequest.set(SubscriptionRequestType('2'))
        tickerRequest.set(MarketDepth(0))
        
        self.addMDType(tickerRequest, '0')
        self.addMDType(tickerRequest, '1')
        self.addMDType(tickerRequest, '2')
        self.addMDType(tickerRequest, '3')
        self.addMDType(tickerRequest, '4')
        self.addMDType(tickerRequest, '5')
        self.addMDType(tickerRequest, '6')
        self.addMDType(tickerRequest, '7')
        self.addMDType(tickerRequest, '8')
        self.addMDType(tickerRequest, '9')
        self.addMDType(tickerRequest, 'A')
        self.addMDType(tickerRequest, 'B')
        self.addMDType(tickerRequest, 'C')
            
        return tickerRequest

    def addMDType(self,tickerRequest, type):
        g0 = MarketDataRequest.NoMDEntryTypes()
        g0.set(MDEntryType(type))
        tickerRequest.addGroup(g0)
