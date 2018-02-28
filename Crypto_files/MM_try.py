# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 13:05:18 2018

@author: Alessandro-Temp

MARKET MAKING TESTS ON CRYPTOS

"""

import pandas as pd
from Requests_module import get_book, get_trades
import matplotlib.pyplot as plt
import numpy as np
import time
import mpl_tweak_module

#Set matplolib features
mpl_tweak_module.set_params()



def stack(v, elem):
    
    #v must be numpy!!

    v_new = np.roll(v,-1)
    v_new[-1] = elem
    
    return v_new
    
#=====================================================================

N = 500
thresh = 0.005

crypto = 'BTC'
fiat = 'EUR'

exchange_1 = 'Kraken' #'Kraken'#'Bitstamp'#'GDAX'
exchange_2 = 'GDAX'

format_1 = 'b-'
format_2 = 'g-'

#=====================================================================


bid_1 = np.zeros(N)
ask_1 = np.zeros(N)

bid_2 = np.zeros(N)
ask_2 = np.zeros(N)

volumes_1 = np.zeros(N)
volumes_2 = np.zeros(N)

#Store Kraken Trades
trades_1 = np.zeros(N)
trades_2 = np.zeros(N)

last_timestamp_ex_1 = 0
last_timestamp_ex_2 = 0


fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)


plt.show()

while len(plt.get_fignums()) != 0: 
    
    last_trade_ex_1, timestamp_ex_1, vol_side_ex_1 = get_trades(crypto, fiat, exchange_1)
    bid_ex_1, ask_ex_1 = get_book(crypto, fiat, exchange_1)    
    
    last_trade_ex_2, timestamp_ex_2, vol_side_ex_2 = get_trades(crypto, fiat, exchange_2)
    bid_ex_2, ask_ex_2 = get_book(crypto, fiat, exchange_2) 

    
    #Stack the new element in the end
    
    bid_1 = stack(bid_1, bid_ex_1)
    ask_1 = stack(ask_1, ask_ex_1)
    
    bid_2 = stack(bid_2, bid_ex_2)
    ask_2 = stack(ask_2, ask_ex_2)
    
    
    #Stack a zero if no new trade is recorded
    if (timestamp_ex_1 != last_timestamp_ex_1):
        
        trades_1 = stack(trades_1, last_trade_ex_1)
        volumes_1 = stack(volumes_1, vol_side_ex_1)
        last_timestamp_ex_1 = timestamp_ex_1
        
    else:
        
        trades_1 = stack(trades_1, 0)
        volumes_1 = stack(volumes_1, 0)
        
     #Stack a zero if no new trade is recorded
    if (timestamp_ex_2 != last_timestamp_ex_2):
        
        trades_2 = stack(trades_2, last_trade_ex_2)
        volumes_2 = stack(volumes_2, vol_side_ex_2)
        last_timestamp_ex_2 = timestamp_ex_2
        
    else:
        
        trades_2 = stack(trades_2, 0)
        volumes_2 = stack(volumes_2, 0) 
        
#    #Remember last recorded trade so that it's not added again     
#    mid_1 = (ask_1 + bid_1)/2
    
    ax1.cla()
    
    x1 = np.where(bid_1 > 0)[0]
    x2 = np.where(bid_2 > 0)[0]
    
    x3 = np.where(trades_1 > 0)[0]
    x4 = np.where(trades_2 > 0)[0]

    
    
    ax1.plot(x2, bid_1[x1], format_1)
    ax1.plot(x2, ask_1[x1], format_1)
    
    ax1.plot(x2, bid_2[x2], format_2)
    ax1.plot(x2, ask_2[x2], format_2)

    ax1.plot(x3, trades_1[x3], 'bo')
    ax1.plot(x4, trades_2[x4], 'rx')
    
    ax1.grid(True)
    
    ax2.cla()    
    
    #Complicated way to align x axes
    ax2.plot(x1, np.zeros(len(x1)), color = 'grey',\
             linestyle = '--', linewidth = 0.3)
    
    ax2.plot(x3, np.cumsum(volumes_1[x3]), format_1)
    ax2.plot(x4, np.cumsum(volumes_2[x4]), format_2)
    
    
    ax2.grid(True)
    
    
    plt.pause(0.01)
    time.sleep(0.6)
    
    
