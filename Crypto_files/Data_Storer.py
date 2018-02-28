# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 15:49:10 2018

@author: Alessandro

CRYPTO DATA RECORDER

- Retrieve Book (10-level depth) and trades (almost simultaneously)
- Update list with fixed length
- when list is filled save as csv in exchange-pair folder and properly named csv

"""
from __future__ import division

import pandas as pd
import numpy as np
from Requests_module import get_trades, get_book_depth
import os
import time
import datetime

#=============================================================================

crypto = 'BTC'
fiat = 'EUR'

exchange = 'Kraken'

#Length of arrays (number of registrations before saving)
N = 1000

#Dataframe columns
colonne = ['Bid_1', 'Bid_2', 'Bid_3', 'Bid_4', 'Bid_5', 'Bid_6', 'Bid_7', 'Bid_8', 'Bid_9', 'Bid_10',                    \
           'Qty_Bid_1', 'Qty_Bid_2', 'Qty_Bid_3', 'Qty_Bid_4', 'Qty_Bid_5', 'Qty_Bid_6', 'Qty_Bid_7', 'Qty_Bid_8', 'Qty_Bid_9', 'Qty_Bid_10', \
           'Ask_1', 'Ask_2', 'Ask_3', 'Ask_4', 'Ask_5', 'Ask_6', 'Ask_7', 'Ask_8', 'Ask_9', 'Ask_10',                    \
           'Qty_Ask_1', 'Qty_Ask_2', 'Qty_Ask_3', 'Qty_Ask_4', 'Qty_Ask_5', 'Qty_Ask_6', 'Qty_Ask_7', 'Qty_Ask_8', 'Qty_Ask_9', 'Qty_Ask_10']

#============================================================================

fPath = os.path.dirname(os.path.abspath(__file__))

savePath = fPath + '\Data\\' + exchange + '-' + crypto + fiat + '\\'

counter = 0
last_timestamp = 0


bid_list = [0]*N
ask_list = [0]*N
           
trades = np.zeros(N)
volumes = np.zeros(N)
timestamps = np.zeros(N)

print 'Start Recording...'

while counter < N:
    
    start = datetime.datetime.now()
    
    last_trade, timestamp, vol_side = get_trades(crypto, fiat, exchange)
    bid, ask = get_book_depth(crypto, fiat, exchange, 10)    
    
    if bid == 0 or ask == 0:
        
        time.sleep(0.3)
        continue
        
    bid_list[counter] = bid
    ask_list[counter] = ask        
        
    
    #Stack UNIX timestamp
    timestamps[counter] = timestamp
            
    if (timestamp != last_timestamp):
        
        trades[counter] = last_trade
        volumes[counter] = vol_side
        last_timestamp = timestamp
        
    else:
        
        trades[counter] = 0
        volumes[counter] = 0

        
    
    if counter == N - 1:
    
        #Create and store dataframe    
        
        df_ask = pd.DataFrame(ask_list)
        df_bid = pd.DataFrame(bid_list)
        df = pd.concat([df_bid, df_ask], axis = 1)
        df.columns = colonne 
        df['Trades'] = trades
        df['Volumes'] = volumes
        df['Timestamp'] = timestamps
          
        df_to_store = df.set_index('Timestamp', drop = True)
        
        fName = datetime.datetime.strftime(datetime.datetime.now(), \
                '%d-%m-%Y-%H.%M.%S')
        df_to_store.to_csv(savePath + fName + '.csv')
        
        print 'Saved', fName
        #Reinitialize for safety purposes
        bid_list = [0]*N
        ask_list = [0]*N
                   
        trades = np.zeros(N)
        volumes = np.zeros(N)
        timestamps = np.zeros(N)

        #But most importantly....
        counter = 0
        
        #Don't wait additional time in this case
        continue
    
    finish = datetime.datetime.now()
    
    if (finish - start).seconds < 1:
        
        time.sleep((1e6 - (finish - start).microseconds)/1e6)
          
    #time.sleep(1)
    
    counter = counter + 1
    



