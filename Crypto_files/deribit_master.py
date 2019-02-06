# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 11:00:58 2019

@author: alforlon

trades+orderbook deribit

"""
from __future__ import division

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.path as mpath
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection
from math import floor
from matplotlib.animation import FuncAnimation
import time
from math import floor

from threading import Thread
from quote_master_deribit import QuoteManager
from trade_master_deribit import TradeManager




N = 50
TIMEOUT = 0.5
WINDOW = 100
MAXSIZE = 15

data =  ['']*N*5

qm = QuoteManager(N, '', timeout = TIMEOUT)
data_thread = Thread(target=qm.work)
data_thread.start()


tm = TradeManager(20, window = WINDOW)
data_thread_trades = Thread(target=tm.work)
data_thread_trades.start()

#%%

def label(xy, text, ax):
    y = xy[1]+0.25   # shift y-value for label so that it's below the artist
    l = ax.text(xy[0]+0.5, y, text, ha="center", family='sans-serif', size=8)
    return l




#fig, ax = plt.subplots()
fig = plt.figure()
ax = fig.add_subplot(111)

fig_2 = plt.figure()
ax_2 = fig_2.add_subplot(111)

grid = np.mgrid[0:5, 0:N].reshape(2,-1).T

patches = []
labels = []

# aggiungi note a sc
for i in range(5*N):
    rect = mpatches.Rectangle(grid[i], 1, 1)
    rect.set_edgecolor('black')
    patches.append(rect)
    l = label(grid[i], data[i], ax)
    labels.append(l)
    
colors = ["white"]*N+["blue"]*int(N/2) + ["white"]*int(N/2) + ["white"]*N + \
         ["white"]*int(N/2) + ["orange"]*int(N/2) + ["white"]*int(N*3/2)
#label(grid[1], "Rectangle")
cmap = matplotlib.cm.get_cmap('BuPu')

collection = PatchCollection(patches, alpha = 0.3)
#collection.set_array(np.array(colors))
ax.add_collection(collection)

#collection.set_edgecolor('b')
collection.set_facecolor(colors)#[(1,1,x) for x in np.arange(60)/60])

#plt.axis('equal')
#plt.axis('off')
ax.set_xlim([0,5])
ax.set_ylim([0,N])
plt.tight_layout()


plt.show()


def coordinates_to_number(x,y):
    
    return int(N*floor(x) + floor(y))



def normalize_vectors(vect_1, vect_2):
    
    vect = vect_1 + vect_2
    
    v = np.array([x if x != '' else 0 for x in vect])
    
    if np.max(v) - np.min(v) < 1e-6:
        return np.zeros(len(v))
    
    v_norm = (v - np.min(v))/(np.max(v)-np.min(v))
    
    return v_norm[:len(vect_1)], v_norm[len(vect_1):]



def normalize_cum_vectors(vect_1, vect_2):
    
    
    # prima vengono riformattati
    v_1 = np.cumsum(np.array([x if x != '' else 0 for x in vect_1]))
    v_2 = np.cumsum(np.array([x if x != '' else 0 for x in vect_2]))
    
    v = np.concatenate([v_1, v_2])
    
    if np.max(v) - np.min(v) < 1e-6:
        return np.zeros(len(v))
    
    v_norm = (v - np.min(v))/(np.max(v)-np.min(v))
    
    return v_norm[:len(vect_1)][::-1], v_norm[len(vect_1):]



def assign_colors(bids, asks):
    
    
    #normalizza tra 0 e 1 i vettori
    norm_bids, norm_asks = normalize_vectors(bids, asks)
    
    norm_cum_bids, norm_cum_asks = normalize_cum_vectors(bids[::-1], asks)
    
    bid_colors = [cmap(x) for x in norm_bids]
    ask_colors = [cmap(x) for x in norm_asks]
    
    bid_cum_colors = [cmap(x) for x in norm_cum_bids]
    ask_cum_colors = [cmap(x) for x in norm_cum_asks]
    
    colorlist = bid_cum_colors + bid_colors + ["white"]*N + \
         ask_colors + ask_cum_colors         
    return colorlist
    

# handles clicks
def onclick(event):


    # get from coordinates number
    ix = coordinates_to_number(event.xdata, event.ydata)
    print(labels[2*N+int(floor(event.ydata))].get_text())
    
    # change color
    new_colors = colors[:]
    new_colors[ix] = 'black'

    collection.set_facecolor(new_colors)

    event.canvas.draw()
    

# handles data updates
def update_book_figure(frame):
    
    # get bid and asks
    prices, bids, asks = qm.get_moving_price_table(N)

    new_colors = assign_colors(bids, asks)
    
    collection.set_facecolor(new_colors)
    fig.canvas.draw()
    
    if prices is None:
        return labels
    
    for i in range(N):
        labels[i+N].set_text(str(bids[i]))
        labels[i+N*2].set_text(str(prices[i]))
        labels[i+N*3].set_text(str(asks[i]))
        
    return labels


def normalize_sizes(v):
    
    vect = np.array(v)
    vect_range = np.max(vect)-np.min(vect)
    return MAXSIZE*(vect - np.min(vect))/vect_range + 8


def update_trade_figure(frame):
    
    prices, qtys, sides, times = tm.get_trades() 
    ax_2.cla()
    ax_2.plot(times, prices, marker='x')
    ax_2.grid(True)
    
    fig_2.canvas.draw()
    
    trade_labels = [None]*WINDOW
    
    fontsizes = [int(x) for x in normalize_sizes(qtys)]
    # aggiorna labels
    for i in range(len(prices)):
        if sides[i] == 'buy':
            trade_labels[i] = ax_2.text(times[i]-10, prices[i]+0.1, qtys[i], ha="center", family='sans-serif', size=fontsizes[i], color = 'green')
        elif sides[i] == 'sell':
            trade_labels[i] = ax_2.text(times[i]-10, prices[i]-0.1, qtys[i], ha="center", family='sans-serif', size=fontsizes[i], color = 'red')
    
    return trade_labels
        
    
        
ani = FuncAnimation(fig, update_book_figure, interval = 1000, blit=True)



# button_press
#cid = fig.canvas.mpl_connect('button_press_event', onclick)

ani_2 = FuncAnimation(fig_2, update_trade_figure, interval = 300, blit=True)

