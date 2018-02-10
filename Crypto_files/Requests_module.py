# -*- coding: utf-8 -*-
"""
Created on Sat Feb 10 15:27:51 2018

@author: Alessandro-Temp

COPY OF CRYPTO HELPER

"""
import requests
import datetime

def get_APIString(crypto, fiat, exchange, kind):
    
    #BITSTAMP
    if exchange == 'Bitstamp':
        
        if kind == 'book':
            
            apiRoot = "https://www.bitstamp.net/api/v2/order_book/"
        
        elif kind == 'trades':
            
            apiRoot = "https://www.bitstamp.net/api/v2/transactions/"
        
        api_String = apiRoot + crypto.lower() + fiat.lower()
        
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
            
        else:
            
            last_trade = float(trades[0]['price'])
            last_timestamp = float(trades[0]['date'])
            

        return last_trade, last_timestamp
    
    
    except:
        
        print (datetime.datetime.now(), 'No answer from', exchange) 
        return 0, 0
    
    


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
        return (0, 0)
    
