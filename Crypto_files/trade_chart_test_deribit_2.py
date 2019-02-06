# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 09:34:06 2019

@author: alforlon

trade chart veloce

"""

from __future__ import division


from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np
from mpl_tweak_module import set_params

from trade_master_deribit import TradeManager
from threading import Thread
import time

set_params()

MAXSIZE = 15
WINDOW = 100

tm = TradeManager(20, window = WINDOW)
data_thread = Thread(target=tm.work)
data_thread.start()

color_dict = {'buy':'green', 'sell':'red'}


#%%
fig = plt.figure()
ax = fig.add_subplot(111)

def normalize_sizes(v):
    
    vect = np.array(v)
    vect_range = np.max(vect)-np.min(vect)
    return MAXSIZE*(vect - np.min(vect))/vect_range + 8

def update_figure(frame):
    
    prices, qtys, sides, times = tm.get_trades() 
    ax.cla()
    ax.plot(times, prices, marker='x')
    
    fig.canvas.draw()
    
    labels = [None]*WINDOW
    
    fontsizes = [int(x) for x in normalize_sizes(qtys)]
    # aggiorna labels
    for i in range(len(prices)):
        
        
        if sides[i] == 'buy':
            labels[i] = plt.text(times[i]-10, prices[i]+0.1, qtys[i], ha="center", family='sans-serif', size=fontsizes[i], color = 'green')
        elif sides[i] == 'sell':
            labels[i] = plt.text(times[i]-10, prices[i]-0.1, qtys[i], ha="center", family='sans-serif', size=fontsizes[i], color = 'red')
            
    return labels
        
    
        
ani = FuncAnimation(fig, update_figure, interval = 300, blit=True)