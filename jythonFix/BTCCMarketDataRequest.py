#!/usr/local/bin/jython
#coding:utf-8

import quickfix.Message as Message
import quickfix.field.MDEntryType as MDEntryType
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
        tickerRequest.set(MarketDepth(2))
        
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
    #  */
    def marketDataIncrementalRequest(self, symbol):
        tickerRequest = quickfix.fix44.MarketDataRequest()
        
        noRelatedSym = quickfix.fix44.MarketDataRequest.NoRelatedSym()
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
        tickerRequest = quickfix.fix44.MarketDataRequest()
        
        noRelatedSym = quickfix.fix44.MarketDataRequest.NoRelatedSym()
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
