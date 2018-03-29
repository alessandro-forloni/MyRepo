#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 15:03:53 2018

@author: alessandro

BITMEX DEPTH CHART

"""

from __future__ import division

import pandas as pd
import datetime 
from Websocket_Master_Class import my_websocket
import websocket
import threading
import time
import matplotlib.pyplot as plt
import numpy as np
import mpl_tweak_module 
import sys


mpl_tweak_module.set_params()


#=============================================================================

marker_mult = 20000
N = 1000

#============================================================================


websocket.enableTrace(True)

#Initialize websocket
my_socket_depth = my_websocket('orderBook10', 'XBTUSD')

wst = threading.Thread(target=my_socket_depth.run_forever)
wst.daemon = True
wst.start()

time.sleep(10)

counter = 0

fig = plt.figure()
depth_ax = fig.add_subplot(111)

plt.show()


print 'Start Recording...\n'


#Here record data
while len(plt.get_fignums()) != 0: 

    try:
    
        start = datetime.datetime.now()   
        
        ts, bids, asks = my_socket_depth.get_data()
        #ts, bids, asks = ('', [1,2], [2,3])
        
        
        bid_levels = np.array([x[0] for x in bids])         
        bid_qtys = np.array([x[1] for x in bids])
        ask_levels = np.array([x[0] for x in asks]) 
        ask_qtys = np.array([x[1] for x in asks])
        
        depth_ax.scatter(np.ones(len(list(bid_levels)))*counter, bid_levels, c = 'b', s = bid_qtys/marker_mult)
        depth_ax.scatter(np.ones(len(list(ask_levels)))*counter, ask_levels, c = 'r', s = ask_qtys/marker_mult)
        
        plt.pause(0.01)
        
        counter = counter + 1
        
        if counter == N:
            
            depth_ax.cla()
            counter = 0
            
        finish = datetime.datetime.now()
        
        if (finish - start).microseconds < 500000:
            
            time.sleep(max((450000 - (finish - start).microseconds)/1e6, 0))
            
            
    # DO THINGS
    except KeyboardInterrupt:
         # quit
         my_socket_depth.ws.close() 
         #sys.exit()
         break


my_socket_depth.ws.close() 