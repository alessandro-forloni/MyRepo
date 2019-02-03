# -*- coding: utf-8 -*-
"""
Created on Sat Feb  2 19:45:41 2019

@author: alforlon
"""

from __future__ import division


from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
from mpl_tweak_module import set_params

from trade_master_deribit import TradeManager
from threading import Thread

set_params()

MAXSIZE = 1000


tm = TradeManager(20, window = 1000)
data_thread = Thread(target=tm.work)
data_thread.start()

color_dict = {'buy':'green', 'sell':'red'}

#%%

fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

def normalize_sizes(v):
    
    vect = np.array(v)
    vect_range = np.max(vect)-np.min(vect)
    return MAXSIZE*(vect - np.min(vect))/vect_range + 2


def update_figure():
    
    ax1.cla()
    
    prices, qtys, sides, times = tm.get_trades() 
    c =  map(color_dict.get, sides)
    ax1.scatter(times, prices, color=c, marker='s', s=normalize_sizes(qtys))
    ax1.grid(True)
    
    ax2.cla()
    
    ax2.plot(times, qtys, marker = 'o', markersize=2)
    
    plt.show()


prices, qtys, sides, times = tm.get_trades() 
c =  map(color_dict.get, sides)
ax1.scatter(times, prices, color=c, marker='s', s=normalize_sizes(qtys))
ax1.grid(True)

# data is reversed
ax2.plot(times, qtys, marker = 'o', markersize=2)#, facecolor = c)

 
plt.show()

#ani = FuncAnimation(fig, update_figure, interval = 300, blit=True)


#%%

# aggiornamento brutale
update_figure()

