# -*- coding: utf-8 -*-
"""
Created on Wed Jan 24 13:38:31 2018

@author: Alessandro

VIX S&P RETURN ANALYSIS

"""

from __future__ import division
import pandas as pd
import os
import datetime
import time
import numpy as np
import matplotlib.pyplot as plt


#VIX EXISTS FROM 2006-02-27

#PARAMS
#=======================================================================

N_days = 90

#=======================================================================

plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', \
               'ytick.color':'green','grid.color':'grey', 'xtick.color':'green',\
               'figure.facecolor':'black', 'figure.edgecolor':'green', 
               'grid.linestyle':'--'})


#Finds the previous nearest to pivot
def nearest_prev(items, pivot):
        return min(items, key = lambda x: abs(x - pivot) if x <= pivot \
                   else abs(x - pivot) + datetime.timedelta(1000))
                   
                   
fPath = os.path.dirname(os.path.abspath(__file__)) + '\\CBOEOptionsData\\'

#List of files in folder
files = [x for x in os.listdir(fPath)]

#List of available days for trading
dates_list = [x[26:36] for x in files]

#List of available days for trading in datetime format
file_dates = [datetime.datetime.strptime(x, '%Y-%m-%d') for x in dates_list]

#For pplotting purposes
x_ticks = [x[26:33] for x in files]

snp = np.zeros(len(files))
vix = np.zeros(len(files))

snp_ahead = np.zeros(len(files))
vix_ahead = np.zeros(len(files))

counter = 0

start = time.time()


print '\nLoading Data...\n'

#Initialize dictionary of dataframes
data = dict()

for f in files:
    
    data[f] = pd.read_csv(fPath + f)


print 'Done in', round(time.time() - start,2)



for f in files:
    
    df = data[f]
    df_vix = df
    
        
    df = df[df['underlying_symbol'] == '^SPX']    
    df_vix = df_vix[df_vix['underlying_symbol'] == '^VIX']


    #Get data
    snp[counter] = (df['underlying_bid_1545'].iloc[0] \
                    + df['underlying_bid_1545'].iloc[0])/2

    vix[counter] = (df_vix['underlying_bid_1545'].iloc[0] \
                    + df_vix['underlying_bid_1545'].iloc[0])/2
                    
    #Get dates
    today = datetime.datetime.strptime(f[26:36], '%Y-%m-%d')
    ideal = today + datetime.timedelta(N_days)
    
    #Look for closest PREVIOUS date
    nearest_date = nearest_prev(file_dates, ideal)
    nearest_date_string = datetime.datetime.strftime(nearest_date,"%Y-%m-%d") 
    
    #Retrieve file name
    ahead_file = 'UnderlyingOptionsEODCalcs_' + nearest_date_string + '.csv'
    
    #Open file
    ahead_data = data[ahead_file]
    ahead_data_vix = ahead_data[ahead_data['underlying_symbol'] == '^VIX']
   
    #Extract Three month ahead price
    snp_ahead[counter] = (ahead_data['underlying_bid_1545'].iloc[0] \
                          + ahead_data['underlying_bid_1545'].iloc[0])/2

    vix_ahead[counter] = (ahead_data_vix['underlying_bid_1545'].iloc[0] \
                          + ahead_data_vix['underlying_bid_1545'].iloc[0])/2
                    
    
    counter = counter + 1

#%%    
#============================================================================

    
data_complete = pd.DataFrame(snp, columns = ['SPX'])
data_complete['VIX'] = vix
data_complete['SPX_ahead'] = snp_ahead
data_complete['VIX_ahead'] = vix_ahead


data_complete['SPX_ret'] = data_complete['SPX_ahead']/data_complete['SPX'].shift(1) - 1
data_complete['VIX_ret'] = data_complete['VIX_ahead']/data_complete['VIX'].shift(1) - 1

data_complete['Date'] = dates_list

#%%
#=============================================================================

fig = plt.figure()

ax1 = fig.add_subplot(121)

plt.scatter(data_complete['SPX_ret'], data_complete['VIX_ret'], cmap = 'Spectral', \
            c = np.arange(0,data_complete.shape[0])/data_complete.shape[0])
            
ax1.plot()
plt.xlabel('SPX Return', color = 'green')
plt.ylabel('VIX Return', color = 'green')
ax1.set_title('SPX vs VIX (90 days) Returns', color = 'green')
plt.grid(True)
cbar = plt.colorbar()
cbar.set_label("Time", color = 'green')

#prepare x_ticks

#Divide into 10 pieces equally spaced
mod_dates = [x[:7] for x in dates_list]
ixs = [int(x) for  x in np.linspace(0.1,0.9,9)*len(file_dates)]
x_ticks = [mod_dates[x] for x in ixs]

#Set ticks
cbar.ax.set_yticklabels(x_ticks, rotation = 45)



thresholds = np.linspace(-0.4,0.4,100)
vix_rets = np.zeros(len(thresholds))

for i in range(0,len(thresholds)):
    
    temp = data_complete['VIX_ret'][data_complete['SPX_ret'] <= thresholds[i]]
    
    if temp.shape[0] > 0:
        
        vix_rets[i] = temp.mean()
        
    else:
        
        vix_rets[i] = 0
        
        

ax2 = fig.add_subplot(122)

ax2.fill_between(thresholds, 0, vix_rets, alpha=0.4, color = 'blue')
ax2.plot(thresholds, vix_rets, color = 'cyan')

plt.xlabel('SPX Return Threshold', color = 'green')
plt.ylabel('Average VIX Return', color = 'green')
ax2.set_title('Average VIX Return for S&P below threshold', color = 'green')
plt.grid(True)


