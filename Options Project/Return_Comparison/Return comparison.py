# -*- coding: utf-8 -*-
"""
Created on Thu Feb 01 18:22:01 2018

@author: Alessandro

"""

import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt

import math
           

#=======================================================================

fPath = os.path.dirname(os.path.abspath(__file__)) 

#List of files in folder
file1 = '\Tail Risk.xlsx'
file2 = '\Option_PnL.xlsx'

#Open Carlo's PnL in the proper way
df1 = pd.read_excel(fPath + file1, sheetname = '2007-2016')
df1['Date'] = df1.index

#Open our pnl
df2 = pd.read_excel(fPath + file2)

#Merge dataframes
df_complete = pd.merge(df1, df2, how = 'inner', on = 'Date')

#Create cumulative pnl
df_complete['Cum_Tail_Risk'] = (df_complete['Tail Risk']+1).cumprod()
df_complete['Cum_Our_strat'] = (df_complete['Daily_Return']+1).cumprod()

#Compute rolling correlatios
corr_1 = pd.rolling_corr(df_complete['Tail Risk'], df_complete['Daily_Return'], \
                     window=130, min_periods = 1)
corr_2 = pd.rolling_corr(df_complete['Tail Risk'], df_complete['Daily_Return'], \
                     window=260, min_periods = 1)
corr_3 = pd.rolling_corr(df_complete['Tail Risk'], df_complete['Daily_Return'], \
                     window=520, min_periods = 1)

#Their sharpe ratio
sharpe_1 = df_complete['Tail Risk'].mean()/df_complete['Tail Risk'].std()*math.sqrt(252)

#Our sharpe
sharpe_2 = df_complete['Daily_Return'].mean()/df_complete['Daily_Return'].std()*math.sqrt(252)

print 'Carlo\'s annualized sharpe:', sharpe_1
print 'Our annualized sharpe:', sharpe_2

#%%
#Plot

#X_ticks frequency
tick_freq = 250


fig = plt.figure()
ax1 = fig.add_subplot(211)
ax1.set_title('Equity Line comparison', color = 'green')


ax1.plot(df_complete['Cum_Tail_Risk'].values)
ax1.plot(df_complete['Cum_Our_strat'].values, 'r-')



#Normalized plot
#ax1.plot(df_complete['Cum_Tail_Risk'].values/np.std(df_complete['Tail Risk'].values))
#ax1.plot(df_complete['Cum_Our_strat'].values/np.std(df_complete['Daily_Return'].values), 'r-')
ax1.grid(True)


x_ticks = [str(x)[:10] for x in df_complete['Date']]

l = plt.legend(['Carlo', 'Our Strategy'], loc = 2)

for text in l.get_texts():
    text.set_color('green')
    
    
    
ax2 = fig.add_subplot(212)
ax2.set_title('Return Correlation')
ax2.plot(corr_1)
ax2.plot(corr_2)
ax2.plot(corr_3)

ax2.grid(True)


l = plt.legend(['Corr 26 Weeks', 'Corr 52 Weeks', 'Corr 104 Weeks'], loc = 4)

for text in l.get_texts():
    text.set_color('green')



#Set Xticks
plt.xticks(np.arange(len(x_ticks[0::tick_freq]))*tick_freq, \
           x_ticks[0::tick_freq], rotation = 45)

plt.show()



