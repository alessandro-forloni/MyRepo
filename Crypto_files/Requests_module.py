# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 15:27:51 2018

@author: Alessandro-Temp

COPY OF CRYPTO HELPER

"""
import requests
import datetime

def get_APIString(crypto, fiat, exchange, kind):
    
    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #BITSTAMP
    if exchange == 'Bitstamp':
        
        if kind == 'book':
            
            apiRoot = "https://www.bitstamp.net/api/v2/order_book/"
        
        elif kind == 'trades':
            
            apiRoot = "https://www.bitstamp.net/api/v2/transactions/"
        
        api_String = apiRoot + crypto.lower() + fiat.lower()
    
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    
    #KRAKEN
    elif exchange == 'Kraken':
        
        #Handle Bitcoin for Kraken
        if crypto == 'BTC':
        
            crypto = 'XBT'
            
            
        
        if kind == 'book':
            
            apiRoot = "https://api.kraken.com/0/public/Depth?pair="
        
        elif kind == 'trades':
            
            apiRoot = "https://api.kraken.com/0/public/Trades?pair="
        
        api_String = apiRoot + crypto + fiat      
        
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    
    #GDAX
    elif exchange == 'GDAX':
        
        if crypto == 'XRP':
            
            #GDAX diesn't have ripple
            return ''
        
        apiRoot = 'https://api.gdax.com/products/'
        
        
        if kind == 'book':
            
             api_String = apiRoot + crypto +'-'+ fiat +'/book?level=1'
        
        elif kind == 'trades':
            
             api_String = apiRoot + crypto +'-'+ fiat +'/trades'
        
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++   
    else:
        
        print('Exchange', exchange, 'not found')
        return ''
    
    
    return api_String    
    




def get_trades(crypto, fiat, exchange):
    
    '''
    
    GET LAST TRADE AND RELATIVE TIMESTAMP (UNIX FORMAT)
    
    '''
    
    
    #Handle Bitcoin for Kraken
    if exchange == 'Kraken' and crypto == 'BTC':
              
            crypto = 'XBT'
         
            
            
    api_String = get_APIString(crypto, fiat, exchange, 'trades')
    
    
    try:
        
        data = requests.get(api_String)
        trades = data.json()
    
        if exchange == 'Kraken':
            
            last_trade = float(trades['result']['X' + crypto + 'Z' + fiat][-1][0])
            last_timestamp = float(trades['result']['X' + crypto + 'Z' + fiat][-1][2])
            side = trades['result']['X' + crypto + 'Z' + fiat][-1][3]
            
            mult = 1*(side == 'b') - 1*(side == 's')
            
            last_volume = float(trades['result']['X' + crypto + 'Z' + fiat][-1][1])*mult
        
        
        
        elif exchange == 'GDAX':
            
            last_trade = float(trades[0]['price'])
            last_timestamp = trades[0]['time']
            side  = trades[0]['side']
            
            mult = 1*(side == 'buy') - 1*(side == 'sell')
            
            last_volume = float(trades[0]['size'])*mult
            
            
            
        #Finish Bitstaaaamp!!!    
        else:
            
            last_trade = float(trades[0]['price'])
            last_timestamp = float(trades[0]['date'])
            last_volume = -float(trades[0]['amount'])*(2*float(trades[0]['type'])-1)
            

        return last_trade, last_timestamp, last_volume
    
    
    except:
        
         adesso = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H:%M:%S')
         print adesso, 'No answer from', exchange, 'for trades'
         return 0, 0, 0
    
    




def get_book(crypto, fiat, exchange):
    
    
     #Handle Bitcoin for Kraken
    if exchange == 'Kraken' and crypto == 'BTC':
              
            crypto = 'XBT'
    
    
    
    api_String = get_APIString(crypto, fiat, exchange, 'book')
    
    try:
        
        data = requests.get(api_String)
        ob = data.json()
    
        if exchange == 'Kraken':
            
            bid = float(ob['result']['X' + crypto + 'Z' + fiat]['bids'][0][0])
            ask = float(ob['result']['X' + crypto + 'Z' + fiat]['asks'][0][0])
            
            
        else:
            
            bid = float(ob['bids'][0][0])
            ask = float(ob['asks'][0][0])
    

        return bid, ask
    
    
    except:
        
        print (datetime.datetime.now(), 'No answer from', exchange) 
        #Return something that clearly shows an issue or handle with exception
        return (0, 0)
   
    
    
    
    
    
def get_trade_history(crypto, fiat, exchange):
    
    
    '''
    
    RETURNS LIST OF TRADES, TIMES AND TYPE (BUY/SELL)
    
    '''
    
    
    
    #Handle Bitcoin for Kraken
    if exchange == 'Kraken' and crypto == 'BTC':
              
            crypto = 'XBT'
         
            
            
    api_String = get_APIString(crypto, fiat, exchange, 'trades')
    
    try:
        
       data = requests.get(api_String)
       trades = data.json()

       if exchange == 'Kraken':
            
           amounts = []
           times = []
           prices =[]
           

           types = []
            
       else:
           
           #Data must be reversed!
           amounts = [float(x['amount']) for x in trades[::-1]]
           times = [float(x['date']) for x in trades[::-1]]
           prices = [float(x['price']) for x in trades[::-1]]
           
           #Notice Buy : 0 - Sell : 1
           #Must be changed to become -1 and 1
           types = [float(x['type']) for x in trades[::-1]]
           

            

       return amounts, times, prices, types
    
    
    except:
        
        print (datetime.datetime.now(), 'No answer from', exchange) 
        return [], [], [], []
  
    
    
    
    
    
    
def get_book_depth(crypto, fiat, exchange, depth):
    
    
     #Handle Bitcoin for Kraken
    if exchange == 'Kraken' and crypto == 'BTC':
              
            crypto = 'XBT'
    
    
    
    api_String = get_APIString(crypto, fiat, exchange, 'book')
    
    try:
        
        data = requests.get(api_String)
        ob = data.json()
    
        if exchange == 'Kraken':
        
            bid_side = ob['result']['X' + crypto + 'Z' + fiat]['bids'][:depth]
            ask_side = ob['result']['X' + crypto + 'Z' + fiat]['asks'][:depth]
            
            #Transpose the result
            z = map(list, zip(*bid_side))[:2]
            #Concatenate lists
            bid_now = reduce(lambda x,y: x+y, z)
    
            # NOW SME FOR THE ASK
            
            #Transpose the result
            d = map(list, zip(*ask_side))[:2]
            #Concatenate lists
            ask_now = reduce(lambda x,y: x+y, d)
    
            
        else:
            
            bid_now = float(ob['bids'][0][0])
            ask_now = float(ob['asks'][0][0])
    

        return [float(x) for x in bid_now], [float(x) for x in ask_now]
    
    
    except:
        
        adesso = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H:%M:%S')
        print adesso, 'No answer from', exchange, 'for book'
        
        return (0, 0)    