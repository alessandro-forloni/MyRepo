# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 10:20:03 2018

@author: Alessandro

STARTING TO DO SOME ANALYSIS ON THE GIVEN DATA

"""
from __future__ import division


import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.decomposition import PCA
from helper_module import nearest
import matplotlib.pyplot as plt
import datetime

plt.rc_context({'axes.edgecolor':'green','axes.facecolor':'black', \
                'ytick.color':'green','grid.color':'grey', 'xtick.color':'green',\
                'figure.facecolor':'black', 'figure.edgecolor':'green', 
                'grid.linestyle':'--'})



#==========================================================================

#Time distance to compute return
time_dist = 90
train_size = 0.8

#=========================================================================


fPath = os.path.dirname(os.path.abspath(__file__)) 

data = pd.read_csv('SPX-VIX_data.csv', index_col = 0)

dates = [datetime.datetime.strptime(x, '%Y-%m-%d') for x in data.index]

snp_returns = np.zeros(data.shape[0])
vix_returns = np.zeros(data.shape[0])


#Compute time_dist returns
for i in range(0,data.shape[0] - time_dist):
    
    today = dates[i]
    
    target_date = today + datetime.timedelta(time_dist)
    
    actual_date = nearest(dates, target_date)
    
    actual_date_str = datetime.datetime.strftime(actual_date, '%Y-%m-%d')
    
    snp_returns[i] = data['SPX'][actual_date_str]/data['SPX'].iloc[i] - 1
    vix_returns[i] = data['VIX'][actual_date_str]/data['VIX'].iloc[i] - 1
               
#Initialize PCA to get data from the VIX curve
pca = PCA(n_components = 3)

#Careful, signs are changed
Z = pca.fit_transform(data.iloc[:,2:9].values)    


#%%
#Build Dataframe of data for linear regression
df = pd.DataFrame(-Z, columns = ['Level', 'Slope', 'Curvature'], index = data.index)

df['Vol-of-Vol'] = data['Vol-of-Vol'].values
#Always let the SPX return be the last of the features
df['SPX-Return'] = snp_returns
  
  
df['VIX-Return'] = vix_returns
  
  
  
#Remove last part where returns are not given
df = df.iloc[:-time_dist,:]
df.dropna(how = 'any', inplace = True)

df.to_csv('Regression_dataset.csv')


sep = int(train_size*df.shape[0])

X_train = df.iloc[:sep,:-1]
y_train = df.iloc[:sep,-1] 

X_test = df.iloc[sep:,:-1]
y_test = df.iloc[sep:,-1] 


#Go with a plain signle regression
lin_reg = LinearRegression()

lin_reg.fit(X_train, y_train)

print 'R squared:', lin_reg.score(X_test, y_test)

#Check how the VIX should react to a -20% move in the SPX
#in different moments across the sample
X_test['SPX-Return'] = -0.2


#%%
x_ticks = X_test.index
tick_freq = 50

fig_regression = plt.figure()

ax1 = fig_regression.add_subplot(211)
ax2 = fig_regression.add_subplot(212)

ax1.set_title('VIX forecasted return with a 20% Loss in the SPX', color = 'green')
   
#Plot returns scatterplot eventually
#ax1.scatter(np.roll(vix_returns, time_dist), vix_returns, cmap = 'Spectral', \
#            c = np.arange(0,data.shape[0])/data.shape[0])



plt.subplot(211)
ax1.plot(data['SPX'][X_test.index.values].values)
ax1.grid(True)

l1 = plt.legend(['S&P 500'])

for text in l1.get_texts():
    text.set_color('green')

plt.xticks(np.arange(len(x_ticks[0::tick_freq]))*tick_freq, \
           x_ticks[0::tick_freq], rotation = 30)
    
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
plt.subplot(212)
ax2.plot(lin_reg.predict(X_test), 'r-')
ax2.grid(True)

l2 = plt.legend(['VIX Return Forecast'])

for text in l2.get_texts():
    text.set_color('green')
    
plt.xticks(np.arange(len(x_ticks[0::tick_freq]))*tick_freq, \
           x_ticks[0::tick_freq], rotation = 30)