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

N = 300
thresh = 0.005

crypto = 'BTC'
fiat = 'USD'

exchange = 'Kraken'#'Bitstamp'#'Kraken'

#=====================================================================


bid_1 = np.zeros(N)
ask_1 = np.zeros(N)
volumes = np.zeros(N)


#Store Kraken Trades
trades = np.zeros(N)


last_timestamp = 0


fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)


plt.show()

while len(plt.get_fignums()) != 0: 
    
    last_trade, timestamp, vol_side = get_trades(crypto, fiat, exchange)
    bid, ask = get_book(crypto, fiat, exchange)    

    
    #Stack the new element in the end
    
    bid_1 = stack(bid_1, bid)
    ask_1 = stack(ask_1, ask)
    
    
    #Stack a zero if no new trade is recorded
    if (timestamp != last_timestamp):
        
        trades = stack(trades, last_trade)
        volumes = stack(volumes, vol_side)
        last_timestamp = timestamp
        
    else:
        
        trades = stack(trades, 0)
        volumes = stack(volumes, 0)
        
    #Remember last recorded trade so that it's not added again     
    mid_1 = (ask_1 + bid_1)/2
    
    ax1.cla()
    
    x1 = np.where(bid_1 > 0)[0]
    x2 = np.where(ask_1 > 0)[0]
    
    x3 = np.where(trades > 0)[0]

    
    
    ax1.plot(x1, bid_1[x1], 'b-')
    ax1.plot(x2, ask_1[x2], 'b-')

    ax1.plot(x3, trades[x3], 'rx')
    
    
    ax1.grid(True)
    
    ax2.cla()    
    
    #Complicated way to align x axes
    ax2.plot(x1, volumes[x3[0]]*np.ones(len(x1)), 'w-')
    ax2.plot(x3, np.cumsum(volumes[x3]), 'g-')
    
    ax2.grid(True)
    
    
    plt.pause(0.01)
    time.sleep(1)
    
    
