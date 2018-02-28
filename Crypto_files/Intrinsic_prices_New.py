# -*- coding: utf-8 -*-
"""
Created on Sun Feb 18 19:33:39 2018

@author: Alessandro

IMPROVING THE DOSCRETIZER BACKTESTING

IDEALLY ABOUT 3000 TRADES NEEDED TO START HAVING A DECENT MEASURE OF HISTORICAL VOL
 
"""

from __future__ import division


import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import Discretizer_Backtesting
import mpl_tweak_module
import datetime

mpl_tweak_module.set_params()

plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', \
               'ytick.color':'green','grid.color':'grey', 'xtick.color':'green',\
               'figure.facecolor':'black', 'figure.edgecolor':'green', 
               'grid.linestyle':'--'})
 
    
def EMA(data,p):
    
    #Data is numpy array!!!
    
    ema = np.zeros(len(data))
    ema[0:p] = np.mean(data[0:p])
    K = 2/(p+1)
    
    for i in range(p, len(data)):
        
        ema[i] = (data[i] - ema[i-1])*K + ema[i-1]
        
        
    return ema

def pnl(lf, sf, trades):
    
    '''
    
    lf, sf are indexes of points when positions are entered
    if one array is longer than the other, the longest is cut
    (that means only closed traded are counted into the pnl)
    
    '''
    
    #Differnce should always be max 1
    if len(lf) > len(sf):
        
        lf = lf[:-1]
        
    elif len(sf) > len(lf):
        
        sf = sf[:-1]
        
        
        
        
    #Compute pnl being always in the market
    
    #Start determining the first position
    start_pos = 1*(min(sf) > min(lf)) - 1*(min(sf) < min(lf))
    
    if start_pos == -1:
        
        PnL = trades[sf[0]] + 2*sum(trades[sf[1:]]) - \
              2*sum(trades[lf[:-1]]) - trades[lf[-1]]
              
    elif start_pos == 1:
        
        PnL = -trades[lf[0]] - 2*sum(trades[lf[1:]]) + \
              2*sum(trades[sf[:-1]]) + trades[sf[-1]]

    else:
        
        print('Error in PnL')
        return 0
    
    return PnL  - 2*len(lf)*9000*0.004



#Continuously in the market
def pnl_line(lf, sf, trades, comm):
    
    pos = 0
    
    cum_pnl = np.zeros(len(trades)) 
    
    
    for i in range(0, len(trades)):
    
        #Enter long and close shorts 
        if (i in lf):
            
            #Pnl cumulated today is cost of openeing new pos + pnl up to yesterday
            # + pnl of closing position
            cum_pnl[i] = -comm*trades[i]*abs(1-pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            pos = 1
            
            
        elif (i in sf):
            
            #Same as before
            cum_pnl[i] = -comm*trades[i]*abs(-1-pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            pos = -1
         
        #Keep position
        else:
            cum_pnl[i] = cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
        
    return cum_pnl 
 
    
# Filtered, so not necessarily always at the market
def pnl_line_filtered(lf, sf, le, se, trades, comm):
    
    #lf and sf are unfiltered signals
    #le and se are filtered signals
    
    
    pos = 0
    
    cum_pnl = np.zeros(len(trades)) 
    
    
    for i in range(0, len(trades)):
    
        #Enter long and close (potential) shorts 
        if (i in le):
            
            #Pnl cumulated today is cost of openeing new pos + pnl up to yesterday
            # + pnl of closing position
            #Occhio alle commissioni in entrata (notial*target di posizione)
            cum_pnl[i] = -comm*trades[i]*abs(1-pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            pos = 1
            
            
        elif (i in se):
            
            #Same as before
            cum_pnl[i] = -comm*trades[i]*abs(-1-pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            pos = -1
            
        #Only close longs    
#        elif(pos > 0 and i in sf):
#            
#            #Same as before
#            cum_pnl[i] = -comm*trades[i]*abs(pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
#            pos = 0
#            
#        #Only close shorts    
#        elif(pos < 0 and i in lf):
#            
#            #Same as before
#            cum_pnl[i] = -comm*trades[i]*abs(pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
#            pos = 0    
            
        #Keep position
        else:
            cum_pnl[i] = cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
        
    return cum_pnl 



#Take profit logic
#On filtered strategy    
def pnl_line_tp(lf, sf, trades, comm, tp):
    
    pos = 0
    entry = 0
    cum_pnl = np.zeros(len(trades)) 
    
    
    for i in range(0, len(trades)):
    
        #Close long wtith take profit
        if(pos > 0 and trades[i] >=  entry + tp):
            
            cum_pnl[i] = -comm*trades[i]*abs(pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            pos = 0
            
        #Close long wtith take profit
        elif(pos < 0 and trades[i] <=  entry - tp):
            
            cum_pnl[i] = -comm*trades[i]*abs(pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            pos = 0   
            
        #Enter long and close (potential) shorts 
        elif (i in le):
            
            cum_pnl[i] = -comm*trades[i]*abs(1-pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            pos = 1
            entry = trades[i]
            
        elif (i in se):
            
            #Same as before
            cum_pnl[i] = -comm*trades[i]*abs(-1-pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            pos = -1
            entry = trades[i]
            
            
        #Only close shorts 
        elif (pos < 0 and i in lf):
            
            #Pnl cumulated today is cost of openeing new pos + pnl up to yesterday
            # + pnl of closing position
            cum_pnl[i] = -comm*trades[i]*abs(pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            pos = 0
            
        #Only close longs    
        elif (pos > 0 and i in sf):
            
            #Same as before
            cum_pnl[i] = -comm*trades[i]*abs(pos) +  cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            pos = 0
            
         
        #Keep position
        else:
            cum_pnl[i] = cum_pnl[i-1] + pos*(trades[i] - trades[i-1])
            
        
    return cum_pnl 
     
#=============================================================================

crypto = 'BTC'
fiat = 'EUR'

exchange = 'Kraken'

base_thresh = 0.01

start = 0
#stop = 2820

long_std = 10000
short_std = 1000

take_profit = 100

comm = 0.002

#============================================================================

fPath = os.path.dirname(os.path.abspath(__file__)) + '\Live\Data\\' + exchange + '-' + crypto + fiat + '\\'
      
fNames = os.listdir(fPath)

dff = pd.read_csv(fPath + fNames[2])


for name in fNames:
    
    try:
        
        temp = pd.read_csv(fPath + name)
        dff = pd.concat([dff,temp])
        
    except:
        print('Couldn\'t open', name)

    
#fName = '18-02-2018-17.56.34.csv'        
#dff.set_index('Timestamp', inplace=True)
#dff['Time'] = [datetime.datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S') for x in dff.index]
#dff['Timestamp'].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))        


fig = plt.figure()
ax1 = fig.add_subplot(111)


    
#if data not in variables
#data = pd.read_csv(fPath + fName)

#trades = dff['Trades'].values
trades = ((dff['Bid_1']+dff['Ask_1'])/2).values
#trades = data['Trades'].values

trades_filtered = trades[np.where(trades != 0)[0]]

df = pd.DataFrame(trades_filtered, columns = ['Trades'])


#Filter with standard deviation
df_returns = (df/df.shift(1) - 1)
std = df_returns.rolling(short_std, min_periods = 1).std() 
std_mean = df_returns.rolling(long_std, min_periods = 1).std() 

std_measure = base_thresh*std/std_mean

n = df.shape[0]

# Initialize objects
# Threshold is expressed in unit points
core = Discretizer_Backtesting.Filter(df, std_measure.values, base_thresh)
    
    
X1 = core.Discretize()
    
#Actualy plotting the result only for the first 500 prices
[lf, sf] = core.visualize_basic_signals(ax1, start , n-1)

#%%


ema = EMA(trades_filtered,5000)

#Filter signals
trades_ema_l = trades[lf] - ema[lf]
trades_ema_s = trades[sf] - ema[sf]

le = lf[np.where(trades_ema_l > 0)[0]]
se = sf[np.where(trades_ema_s < 0)[0]]

e_line = pnl_line_filtered(lf, sf, le, se, trades, comm)
e_line_unfiltered = pnl_line(lf, sf, trades, comm)

print('PnL:', round(e_line[-1],2))  
print('Number of trades:', len(le) + len(se))
print('Traded Vol:', 8500*1.25*(len(le) + len(se)))  


ax1.plot(ema[start:n-1])

ax2 = ax1.twinx()

ax2.plot(e_line)
ax2.plot(e_line_unfiltered)

ax2.tick_params('y', colors='green')
#ax1.plot(dff['Bid_1'].values)
#ax1.plot(dff['Ask_1'].values)