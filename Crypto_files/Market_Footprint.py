# -*- coding: utf-8 -*-
"""
Created on Sun Feb 11 12:04:38 2018

@author: Alessandro-Temp

MARKET FOOTPRINT CHART FOR CRYPTO ASSETS
"""

from Requests_module import get_trade_history
import numpy as np
import matplotlib.pyplot as plt
import time
import mpl_tweak_module

#Set matplolib features
mpl_tweak_module.set_params()

#==================================================================

crypto = 'BTC'
fiat = 'USD'

exchange = 'Bitstamp'

#==================================================================

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)


while len(plt.get_fignums()) != 0: 

    #Retrieve info about the last hour of trading
    qtys,times,levels,sides = get_trade_history(crypto, fiat, exchange)
    
    #Modify sides to become -1 and 1s
    bs = -(np.array(sides)*2 - 1)
    
    #simple start: plot cumsum of vol*side
    cum_vol = np.cumsum(np.array(qtys)*bs)
    
    ax1.cla()
    ax1.plot(levels)
    ax1.grid(True)
    
    ax2.cla()
    ax2.plot(cum_vol, 'r--')
    ax2.grid(True)
    
    
    plt.pause(0.01)
    time.sleep(1)