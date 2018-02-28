# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 19:33:39 2018

@author: Alessandro

ANALYZING THE SPREAD RESULTS
 
"""
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
#import mpl_tweak_module


#mpl_tweak_module.set_params()

plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', \
               'ytick.color':'green','grid.color':'grey', 'xtick.color':'green',\
               'figure.facecolor':'black', 'figure.edgecolor':'green', 
               'grid.linestyle':'--'})
 
    

#=============================================================================

date = '27-02'
#=============================================================================

fPath = os.path.dirname(os.path.abspath(__file__)) + '\Data\\' + date + '\\'
      
fNames = os.listdir(fPath)

dff = pd.read_csv(fPath + fNames[1])


for name in fNames:
    
    try:
        
        temp = pd.read_csv(fPath + name)
        dff = pd.concat([dff,temp])
        
    except:
        
        print('Couldn\'t open', name)

#filter out moments when there is no trading
dff = dff[dff['Bid_1'] != 0]

mid_1 = (dff['Bid_1'] + dff['Ask_1']).values/2
mid_2 = (dff['Bid_2'] + dff['Ask_2']).values/2

#%%
fig = plt.figure()

ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)



ax1.plot(dff['Bid_1'].values, 'b-')
ax1.plot(dff['Ask_1'].values, 'b-')
ax1.plot(dff['Bid_2'].values, 'r-')
ax1.plot(dff['Bid_2'].values, 'r-')

ax1.grid(True)

ax2.plot(mid_1 - mid_2, 'r-')
ax2.plot(np.zeros(dff.shape[0]), 'g--')

ax2.grid(True)




ax2.plot()