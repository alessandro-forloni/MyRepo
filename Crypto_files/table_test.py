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

from threading import Thread
from quote_master import QuoteManager





N = 40
PAIR = 'XBTEUR'
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


collection = PatchCollection(patches, alpha = 0.3)
#collection.set_array(np.array(colors))
ax.add_collection(collection)

collection.set_edgecolor('k')
collection.set_facecolor(colors)#[(1,1,x) for x in np.arange(60)/60])

#plt.axis('equal')
#plt.axis('off')
plt.xlim([0,5])
plt.ylim([0,N])
plt.tight_layout()

plt.show()

def coordinates_to_number(x,y):
    
    return int(N*floor(x) + floor(y))


# handles clicks
def onclick(event):

    
    print(event.xdata, event.ydata)

    # get from coordinates number
    ix = coordinates_to_number(event.xdata, event.ydata)

    # change color
    new_colors = colors[:]
    new_colors[ix] = 'black'

    collection.set_facecolor(new_colors)

    event.canvas.draw()

# handles data updates
def update(frame):
    
    # get bid and asks
    prices, bids, asks = qm.get_price_table(N)
    
    if prices is None:
        return labels
    
    for i in range(N):
        labels[i+N].set_text(str(bids[i]))
        labels[i+N*2].set_text(str(prices[i]))
        labels[i+N*3].set_text(str(asks[i]))
        
    return labels

# button_press
cid = fig.canvas.mpl_connect('button_press_event', onclick)
ani = FuncAnimation(fig, update, interval = 300, blit=True)






 
    

