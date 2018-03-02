# -*- coding: utf-8 -*-
"""
Created on Thu Mar  1 14:53:42 2018

@author: Alessandro

Updated MM_try_2

"""

import pandas as pd
from Requests_module import get_book, get_trades, get_book_depth
import matplotlib.pyplot as plt
import numpy as np
import time

plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', \
               'ytick.color':'green','grid.color':'grey', 'xtick.color':'green',\
               'figure.facecolor':'black', 'figure.edgecolor':'green', 
               'grid.linestyle':'--'})

#Set matplolib features




def stack(v, elem):
    
    #v must be numpy!!

    v_new = np.roll(v,-1)
    v_new[-1] = elem
    
    return v_new
    
#=====================================================================

N = 500

depth = 3

crypto = 'BTC'
fiat = 'EUR'

exchange_1 = 'Kraken' #'Kraken'#'Bitstamp'#'GDAX'


format_1 = 'b-'
format_2 = 'g-'

#=====================================================================


bid_1 = np.zeros(N)
ask_1 = np.zeros(N)

bid_side = np.zeros(N)
ask_side = np.zeros(N)

volumes_1 = np.zeros(N)


#Store Kraken Trades
trades_1 = np.zeros(N)

last_timestamp_ex_1 = 0



fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

ax3 = ax1.twinx()
ax4 = ax2.twinx()

plt.show()

while len(plt.get_fignums()) != 0: 
    
    last_trade_ex_1, timestamp_ex_1, vol_side_ex_1 = get_trades(crypto, fiat, exchange_1)
    
    #Da questa richiesta esce una lista con [livelli, quantità]
    bid, ask = get_book_depth(crypto, fiat, exchange_1, 3)   

   
    
    
    #Stack the new element in the end
    
    bid_1 = stack(bid_1, bid[0])
    ask_1 = stack(ask_1, ask[0])
 
    #Attacca anche elementi depth
    bid_side =  stack(bid_side, np.sum(bid[depth:]))
    ask_side =  stack(ask_side, np.sum(ask[depth:]))
    
    
    #Stack a zero if no new trade is recorded
    if (timestamp_ex_1 != last_timestamp_ex_1):
        
        trades_1 = stack(trades_1, last_trade_ex_1)
        volumes_1 = stack(volumes_1, vol_side_ex_1)
        last_timestamp_ex_1 = timestamp_ex_1
        
    else:
        
        trades_1 = stack(trades_1, 0)
        volumes_1 = stack(volumes_1, 0)

    
    ax1.cla()
    ax3.cla()
    
    
    x1 = np.where(bid_1 > 0)[0]
    x3 = np.where(trades_1 > 0)[0]
    
    
    ax1.plot(x1, bid_1[x1], format_1)
    ax1.plot(x1, ask_1[x1], format_1)
    
    ax3.plot(x1, bid_side[x1] - ask_side[x1], 'g-')
    ax3.plot(x1, np.zeros(len(x1)), 'r--')
    
    ax3.tick_params('y', colors='green')
    

    ax1.plot(x3, trades_1[x3], 'rx')

    ax1.grid(True)
    
    ax2.cla()    
    ax4.cla()
    
    #Complicated way to align x axes
    ax2.plot(x1, np.zeros(len(x1)), color = 'grey',\
             linestyle = '--', linewidth = 0.3)
    
    ax2.plot(x3, np.cumsum(volumes_1[x3]), format_1)
    ax4.plot(x1, bid_side[x1] + ask_side[x1], 'g-')
    
    ax4.tick_params('y', colors='green')
    ax4.grid(True)

    
    plt.pause(0.01)
    time.sleep(0.8)
