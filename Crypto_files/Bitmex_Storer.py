#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 27 09:18:47 2018

@author: alessandro

STORING BITMEX ORDERBOOK

"""
from __future__ import division

import pandas as pd
import datetime 
from Websocket_Master_Class import my_websocket
import websocket
import threading
import time
import os
import numpy as np


websocket.enableTrace(True)

#============================================================================

fPath = os.path.dirname(os.path.abspath(__file__))

savePath = fPath + '/Data/Bitmex_XBTUSD/'

N = 2000

#============================================================================


colonne = ['Bid_1', 'Bid_2', 'Bid_3', 'Bid_4', 'Bid_5', 'Bid_6', 'Bid_7', 'Bid_8', 'Bid_9', 'Bid_10',                    \
           'Qty_Bid_1', 'Qty_Bid_2', 'Qty_Bid_3', 'Qty_Bid_4', 'Qty_Bid_5', 'Qty_Bid_6', 'Qty_Bid_7', 'Qty_Bid_8', 'Qty_Bid_9', 'Qty_Bid_10', \
           'Ask_1', 'Ask_2', 'Ask_3', 'Ask_4', 'Ask_5', 'Ask_6', 'Ask_7', 'Ask_8', 'Ask_9', 'Ask_10',                    \
           'Qty_Ask_1', 'Qty_Ask_2', 'Qty_Ask_3', 'Qty_Ask_4', 'Qty_Ask_5', 'Qty_Ask_6', 'Qty_Ask_7', 'Qty_Ask_8', 'Qty_Ask_9', 'Qty_Ask_10']


#Initialize websocket
my_socket = my_websocket('orderBook10', 'XBTUSD')

wst = threading.Thread(target=my_socket.run_forever)
wst.daemon = True
wst.start()

time.sleep(10)

counter = 0


print 'Start Recording...\n'


bid_list = [0]*N
ask_list = [0]*N
ts_list = [0]*N 
recording_time_list = [0]*N      



#Here record data
while True:

    start = datetime.datetime.now()   
    
    ts, bids, asks = my_socket.get_data()
    
    #Stack levels and sizes
    bid_formatted = [x[0] for x in bids] + [x[1] for x in bids]
    ask_formatted = [x[0] for x in asks] + [x[1] for x in asks]
        
    recording_time = datetime.datetime.strftime(datetime.datetime.now(), \
                     '%d-%m-%Y-%H:%M:%S.%f')
    
    
    bid_list[counter] = bid_formatted
    ask_list[counter] = ask_formatted
    
    ts_list[counter] = ts
    recording_time_list[counter] = recording_time
    
    
    print ts, recording_time
    print bid_formatted[:3], ask_formatted[:3]
    
    if counter == N - 1:
    
        #Create and store dataframe    
        
        df_ask = pd.DataFrame(ask_list)
        df_bid = pd.DataFrame(bid_list)
        
        #concatenate bid and ask dataframes
        df = pd.concat([df_bid, df_ask], axis = 1)
        df.columns = colonne 
        
        #Add timestamps
        df['Timestamp'] = recording_time_list
        df['Original_Timestamp'] = ts_list
        
        
        df_to_store = df.set_index('Timestamp', drop = True)
        
        fName = datetime.datetime.strftime(datetime.datetime.now(), \
                '%d-%m-%Y-%H.%M.%S')
        df_to_store.to_csv(savePath + fName + '.csv')
        
        print 'Saved', fName
        #Reinitialize for safety purposes
        bid_list = [0]*N
        ask_list = [0]*N
                   
        ts_list = [0]*N 
        recording_time_list = [0]*N  


        #But most importantly....
        counter = 0
        
        continue
     
    counter = counter + 1
        
    finish = datetime.datetime.now()
    
    if (finish - start).seconds < 1:
        
        time.sleep((999900 - (finish - start).microseconds)/1e6)
             
    
    
my_socket.ws.close() 
