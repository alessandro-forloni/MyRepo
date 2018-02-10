# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.

XRP ARB between Bitstamp and Kraken

"""

import pandas as pd
from Requests_module import get_book, get_trades
import matplotlib.pyplot as plt
import numpy as np
import time


plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', \
                'ytick.color':'green','xtick.color':'green',       \
                'grid.color':'grey', 'grid.linestyle':'--'})

my_color = 'green'


def stack(v, elem):
    
    #v must be numpy!!

    v_new = np.roll(v,-1)
    v_new[-1] = elem
    
    return v_new
    
#=====================================================================

N = 300
thresh = 0.005

#=====================================================================


crypto = 'XRP'
fiat = 'USD'

bid_1 = np.zeros(N)
bid_2 = np.zeros(N)

ask_1 = np.zeros(N)
ask_2 = np.zeros(N)

#Store Kraken Trades
trades_b = np.zeros(N)
trades_k = np.zeros(N)

last_timestamp_b = 0
last_timestamp_k = 0


fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)


plt.show()

while len(plt.get_fignums()) != 0: 
    
    last_trade_bitstamp, timestamp_b = get_trades(crypto, fiat, 'Bitstamp')
    last_trade_kraken, timestamp_k = get_trades(crypto, fiat, 'Kraken')
    bid_stamp, ask_stamp = get_book(crypto, fiat, 'Bitstamp')
    bid_kraken, ask_kraken = get_book(crypto, fiat, 'Kraken')
    

    
    #Stack the new element in the end
    
    bid_1 = stack(bid_1, bid_stamp)
    bid_2 = stack(bid_2, bid_kraken)
    ask_1 = stack(ask_1, ask_stamp)
    ask_2 = stack(ask_2, ask_kraken)
    
    #Stack a zero if no new trade is recorded
    
    if (timestamp_b != last_timestamp_b):
        
        trades_b = stack(trades_b, last_trade_bitstamp)
        last_timestamp_b = timestamp_b
        
    else:
        trades_b = stack(trades_b, 0)
        
        
    if (timestamp_k != last_timestamp_k):
        
        trades_k = stack(trades_k, last_trade_kraken)
        last_timestamp_k = timestamp_k
        
    else:
        trades_k = stack(trades_k, 0)
        
    #Remember last recorded trade so that it's not added again
    
     
    mid_1 = (ask_1 + bid_1)/2
    mid_2 = (ask_2 + bid_2)/2
    
    delta = (mid_2 - mid_1)/mid_1
    
    ax1.cla()
    
    x11 = np.where(bid_1 > 0)[0]
    x12 = np.where(bid_2 > 0)[0]
    x21 = np.where(ask_1 > 0)[0]
    x22 = np.where(ask_2 > 0)[0]
    
    x3 = np.where(trades_b > 0)[0]
    x4 = np.where(trades_k > 0)[0]
    
    
    ax1.plot(x11, bid_1[x11], 'b-')
    ax1.plot(x21, ask_1[x21], 'b-')
    
    ax1.plot(x12, bid_2[x12], 'r-')
    ax1.plot(x22, ask_2[x22], 'r-')
    
    ax1.plot(x3, trades_b[x3], 'bo')
    ax1.plot(x4, trades_k[x4], 'rx')
    
    
    ax1.grid(True)
    
    ax2.cla()    
    ax2.plot(x11, delta[x11], 'g-')
    ax2.plot(x11, thresh*np.ones(len(x11)), 'r--')
    ax2.plot(x11, -thresh*np.ones(len(x11)), 'r--')
    
    ax2.grid(True)
    
    
    plt.pause(0.01)
    time.sleep(1)
    
    