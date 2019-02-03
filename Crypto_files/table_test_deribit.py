# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 14:35:21 2019

@author: alforlon


TABLE TEST

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





N = 50
PAIR = 'BTCEUR'
TIMEOUT = 2

data =  ['']*N*5

qm = QuoteManager(N, PAIR, timeout = TIMEOUT)
data_thread = Thread(target=qm.work)
data_thread.start()



def label(xy, text):
    y = xy[1]+0.25   # shift y-value for label so that it's below the artist
    l = plt.text(xy[0]+0.5, y, text, ha="center", family='sans-serif', size=8)
    return l


fig, ax = plt.subplots()
grid = np.mgrid[0:5, 0:N].reshape(2,-1).T

patches = []
labels = []
# aggiungi note a sc
for i in range(5*N):
    rect = mpatches.Rectangle(grid[i], 1, 1)
    rect.set_edgecolor('black')
    patches.append(rect)
    l = label(grid[i], data[i])
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
plt.xlim([0,5])
plt.ylim([0,N])
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
    
#    colorlist = ["white"]*N + bid_colors + ["white"]*N + \
#         ask_colors + ["white"]*N
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
def update(frame):
    
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
#        labels[0].set_text('')   
    return labels

# button_press
cid = fig.canvas.mpl_connect('button_press_event', onclick)
ani = FuncAnimation(fig, update, interval = 300, blit=True)






 
    

