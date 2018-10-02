# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 20:29:01 2018

@author: alex_

PLAY WITH REUTERS DATA

"""

import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
import math
import os

f_path = os.path.dirname(os.path.abspath(__file__))

print('\nCarico i Dati...')

df_iterator_1 = pd.read_csv(os.path.join(f_path, 'debug_80000-Crossover_strategy_on_FBTP.xls'), sep = ";", skiprows = 1, chunksize = 9000000, index_col = 0)
df_iterator_2 = pd.read_csv(os.path.join(f_path, 'debug_10000-Crossover_strategy_on_FGBL.xls'), sep = ";", skiprows = 1, chunksize = 9000000, index_col = 0)

counter_stop = 3

counter = 0
for chunk in df_iterator_1:
    
    df_1 = chunk
    counter = counter + 1
    
    if counter == counter_stop:
        break
    
counter = 0

for chunk in df_iterator_2:
    
    df_2 = chunk
    counter = counter + 1
    
    if counter == counter_stop:
        break
    

#%%
# Merge dataframes
final_df = df_1.join(df_2, how = 'outer', lsuffix = '_l', rsuffix = '_r')
df = final_df[['price_l', 'price_r']]
df.dropna(how = 'any', inplace = True)

#%%
list_of_evil_values = ['NEWPOS: ' + str(x) for x in range(-100,100)]

df.replace(list_of_evil_values, np.nan, inplace = True)

df.fillna(method = 'ffill', inplace = True)


df['price_l'] = df['price_l'].apply(lambda x: float(x))
df['price_r'] = df['price_r'].apply(lambda x: float(x))


#%%
# Calcola segnale
period = 3600

df_ema = df.ewm(span = period, min_periods = 1).mean()
df_norm = df/df_ema
df_diff = df_norm.iloc[:,0] - df_norm.iloc[:,1]

df_signal = df_diff/df_diff.rolling(period, min_periods = 1).std()

#%%

print('\nGenero Segnali..')

signal = df_signal.values
prices = df.values

thresh_up = 4
thresh_down = -4

record_pos = np.zeros(len(signal))
 
pos = 0

# Generate signals
for i in tqdm(range(period,len(signal)-1)):
    
    # Eventually filter on time
    if signal[i] < thresh_down and pos <= 0:
        
        #order_signals[i+1] = 1
        pos = 1
        
    elif signal[i] > thresh_up and pos >= 0:
        
        #order_signals[i+1] = -1
        pos = -1
        
    elif signal[i] > 0 and pos > 0:
        
        #order_signals[i+1] = -1
        pos = 0
        
    elif signal[i] < 0 and pos < 0:
        
        #order_signals[i+1] = -1
        pos = 0
        
    record_pos[i] = pos


#%%        
# Calculate PnL
cum_pnl = np.zeros(len(record_pos))
pnl = np.zeros(len(record_pos))

comm = 6


print('\nCalcolo PnL...')

ct_size_1 = 5
ct_size_2 = 25

# 40 h circa 5 giorni
vol_period = 3600*40

for i in tqdm(range(1,len(record_pos))):
    
#    vol_1 = ct_size_1*np.std(prices[max(0,i-vol_period):i,0])
#    vol_2 = ct_size_2*np.std(prices[max(0,i-vol_period):i,1])
    
    qty_2 = 1
    qty_1 = 1#round(qty_2*vol_2/vol_1)
    
    # Aggiungi commissioni
    pnl[i] = record_pos[i-1]*(qty_1*(prices[i,0]-prices[i-1,0])*ct_size_1 - \
                              qty_2*(prices[i,1]-prices[i-1,1])*ct_size_2) - \
                              comm*(abs(record_pos[i] - record_pos[i-1]))
    cum_pnl[i] = cum_pnl[i-1] + pnl[i]
      
    
print('\nStart:', df.index[0])
print('Finish:', df.index[-1])

print('\n\nFinal PnL:', cum_pnl[-1])
print('Sharpe-Ratio:', pnl.mean()/pnl.std()*math.sqrt(252*86400))
print('\n')

fig = plt.figure()    
ax = fig.add_subplot(111)

ax.plot(cum_pnl)

plt.show()