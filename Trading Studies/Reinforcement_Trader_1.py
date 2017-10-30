#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 23 20:38:08 2017

@author: ale

Try some reinforcement learning trading:
    
    - Input is series of prices with lag
    - Eventually indicators/MAs
    - Learns randomly
    - Classifies by P&L/Sharpe ratio metric
    - Mega optimization time I guess
    - Consider ranking on both OOS performance 
      and consistency between IS and OOS.
      
"""
import pandas as pd
import numpy as np
import Manual_Network
import Backtest

max_lag = 10
N_out = 5     #N_out strictly smaller than max_lag
N_epochs = 10
N_networks = 18 #Ideally multiple of 3

#Network_size
layer_sizes = [max_lag, 5, 3]

##########################################################





##########################################################

fName = '/home/ale/Documenti/Trading Studies/Data/FIB_Data_New.xlsx'
data = pd.read_excel(fName, Sheetname = '1M')

#Get Deltas
data['change'] = (data['Close']-data['Open'])/5
#data['change'] = data['Close']/data['Close'].shift(1)-1
#data['range'] = data['High']-data['Open']



df_temp = pd.DataFrame(data['Date'])
df_temp['time'] = data['Time']
df_temp['change'] = data['change']
df_temp['volume'] = data['Vol']
df_temp['close'] = data['Close']
df_temp['open'] = data['Open']

#Create Lags onwards and backwards
for i in range(1,max_lag+1):
    
    df_temp['change-'+str(i)] = df_temp['change'].shift(i)
    
    #Onward lags for output
    df_temp['change-'+str(i)+'-out'] = df_temp['change'].shift(-i)
    #df_temp['volume-'+str(i)] = df_temp['volume'].shift(i)
    


#Eliminate first max_lag elements of the day    
i = 1

while i < df_temp.shape[0]:
    
    if((df_temp['Date'][i]-df_temp['Date'][i-1]).total_seconds() > 0):
        
        #Remove previous and following max_lag observations
        for j in range(0,max_lag*2):
            df_temp = df_temp.drop(i-max_lag)
            i = i + 1
           
    i = i + 1
    
df_temp = df_temp.dropna(how = 'any')

#Create new index
dates = [str(x)[:10].replace('-','') for x in df_temp['Date']]
times = [str(x)[:5].replace(':','') for x in df_temp['time']]
new_index = [x+'-'+y for x,y in zip(dates,times)]

#Create and fill new dataframe
df = pd.DataFrame(index = new_index)


for i in range(1,max_lag+1):
    
    df['change-'+str(i)] = df_temp['change-'+str(i)].values
    
    
    #df['volume-'+str(i)] = df_temp['volume-'+str(i)].values




##Create output21
out = df_temp['change']

for i in range(1,N_out+1):
        
    out = out + df_temp['change-'+str(i)+'-out']
#out = df['return'] + df['return'].shift(-1)+ \
#      df['return'].shift(-2) + df['return'].shift(-3)+ \
#      df['return'].shift(-4)
#      
y = (out >= 0)*1
#
#y = (df_temp['change'] > 0)*1



#Clear Memory
#del df_temp
del data
del new_index
del times
del dates
###X_train, X_test, y_train, y_test = train_test_split(df, y, 
##                           test_size=0.2, random_state=42)
#
sep = int(0.8*df.shape[0])

#Normalize
x_mean = df.iloc[:sep,:].mean()
x_std = df.iloc[:sep,:].std()
X_train = df.iloc[:sep,:]#(df.iloc[:sep,:]-x_mean)/x_std
X_test = df.iloc[sep:,:]#(df.iloc[sep:,:]-x_mean)/x_std
y_train = y.iloc[:sep]
y_test = y.iloc[sep:]

#For backtesting
out_train = out.iloc[:sep]
out_test = out.iloc[sep:]

print('Finished pre-processing, now playing....')

#%%

# NEURAL TRADING!

#NETWORK FOR THE MOMENT MUST HAVE 3 LAYERS!
#Last matrix is actually a COLUMN vector!

best_acc = 0

sigma = 5
sigma_u = 0.1

layers_1 = sigma*np.random.randn(layer_sizes[0], layer_sizes[1], N_networks)
layers_2 = sigma*np.random.randn(layer_sizes[1], layer_sizes[2], N_networks)
layers_3 = sigma*np.random.randn(layer_sizes[2], 1, N_networks)

for ep in range(0,N_epochs):
    
    PnL = np.zeros(N_networks)
    
    for i in range(0,N_networks):
        
        M1 = layers_1[:,:,i] 
        M2 = layers_2[:,:,i] 
        M3 = layers_3[:,:,i] 
    
        NN = Manual_Network.my_network(M1, M2, M3)
        
        y_cap = NN.predict(X_train)
        
        #PnL[i] = Backtest.Backtester.sharpe_performance(y_cap,out_test)
        PnL[i] = sum(y_cap == y_train)/len(y_cap)
        
    
    #Now Update weights
    #Sort based on performance  
    pnls = np.flip(np.sort(PnL), axis = 0)
    ix = np.flip(np.argsort(PnL), axis = 0)
    
    #Separate things to regenerate
    sep2 = round(N_networks/3)
    
    change_indexes = ix[sep2:sep2*2]
    new_indexes = ix[sep2*2:]
    #Create noise
    noise_1 = sigma_u*np.random.randn(M1.shape[0], M1.shape[1], len(change_indexes))
    noise_2 = sigma_u*np.random.randn(M2.shape[0], M2.shape[1], len(change_indexes))
    noise_3 = sigma_u*np.random.randn(M3.shape[0], M3.shape[1], len(change_indexes))
    
    for j in range(0,len(change_indexes)):
        
        #Update worst 60% of cases
        layers_1[:,:,change_indexes[j]] = layers_1[:,:,j % sep2] + noise_1[:,:,j]
        layers_2[:,:,change_indexes[j]] = layers_2[:,:,j % sep2] + noise_2[:,:,j]
        layers_3[:,:,change_indexes[j]] = layers_3[:,:,j % sep2] + noise_3[:,:,j]
    
    #Regenerate other third
    for j in range(0,len(new_indexes)):
        
        
        layers_1[:,:,new_indexes[j]] = sigma*np.random.randn(layer_sizes[0], layer_sizes[1])
        layers_2[:,:,new_indexes[j]] = sigma*np.random.randn(layer_sizes[1], layer_sizes[2])
        layers_3[:,:,new_indexes[j]] = sigma*np.random.randn(layer_sizes[2], 1)
    
    print('Epoch number', ep+1, 'Average Accuracy:', round(pnls.mean(),4), 'Best Accuracy:', round(pnls[0],4))        

# Oppure considera ipotesi di agggiornare 1/3 e rigenerane 1/3
# And then vector to keep track of evolution

#%%

print('\nFinished training, now evaluate OOS...')
#Now take best networks and evaluate OOS:
PnL2 = np.zeros(N_networks)  
loss = np.zeros(N_networks) 
n_trades = np.zeros(N_networks) 
 
for i in range(0,N_networks):
    
    M1 = layers_1[:,:,i] 
    M2 = layers_2[:,:,i] 
    M3 = layers_3[:,:,i] 
    
    NN = Manual_Network.my_network(M1, M2, M3)
        
    y_cap = NN.predict(X_train)
    PnL[i] = Backtest.Backtester.pnl_performance(y_cap,out_train)
    n_trades[i] = sum(y_cap)
    
    y_cap = NN.predict(X_test)
    PnL2[i] = Backtest.Backtester.pnl_performance(y_cap,out_test)
    
   
    #Compute loss (Adding one to avoid division by zero)
    loss[i] = round(100*(PnL2[i] - PnL[i])/abs(PnL[i]+1),2)
    
justosee = pd.DataFrame(PnL, columns = ['IS'])
justosee['OOS'] = PnL2
justosee['Loss'] = loss
# In sample number of trades
justosee['Number of trades'] = n_trades

print('\nAverage OOS performance loss:', round(loss.mean()), '%')