# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 13:12:34 2018

@author: Alessandro

IMPLEMENTATION OF WRC STEPWISE TEST

"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math


#=============================================================================

#1 - Test levels
alpha = 0.01

#Number of random bootstrap samples
n_rand = 10000

#=============================================================================

fName_Strats = 'strategies3.csv'
strats = pd.read_csv(fName_Strats)
#
#
#fName = 'Analysis_all_strategies_2018-02-23_report_2018-02-25_07_29.xlsx'     
#df = pd.read_excel(fName, sheetname = 'PnLDailyEqualRisk', skiprows = 2)
#
#temp =  df.iloc[:,1:]
#temp.iloc[0,:] = 100000
#temp2 = temp.cumsum()
#
#strats = temp2/temp2.shift(1) - 1
#strats.dropna(how = 'any', inplace = True)

strats = strats.iloc[:450, :]

#%%


#fig = plt.figure()
#ax1 = fig.add_subplot(211)
#ax2 = fig.add_subplot(212)

N = strats.shape[0]

good_strats = []

strats_sharpe = strats.mean()/strats.std()
strats_means = strats.mean()

#Standard deviation of the mean
strats_std = strats.std()/math.sqrt(N)

#Just to enter in the stepwise cycle
n_rejected = 1000


strats_ix = [x for x in strats_sharpe.index]


statistics = np.zeros(n_rand)


while n_rejected != 0:
    
    #Boostrapping for c
    for i in range(0,n_rand):
        
        #Select random lines
        v = np.random.randint(0,100,int(math.sqrt(N)))
        
        #Create boostrapped matrices to compute staistically relevant c
        bootstrapped_mat = strats.iloc[v,:][strats_ix]
        
        #Save the max of all statistics, carefult st of mean is sigma/sqrt(n)
        statistics[i] = max(bootstrapped_mat.mean()/bootstrapped_mat.std())*math.sqrt(int(math.sqrt(N)))
        
           
    #If aplha = 0.05 set the percentile value to 95
    #Strats ix is a list of names of strategies that are still tested
    c = np.percentile(statistics, 100*(1-alpha))#(strats_sharpe[strats_ix], 100*(1-alpha))
    
    #Build conf intervals lower bound
    lbs = strats_means[strats_ix] - strats_std[strats_ix]*c
    
    #Per ora solo primo step
    res = lbs[lbs > 0]
    rejected = [x for x in res.index]
    
    #Update list of good strategies
    good_strats = good_strats + rejected
    
    #Update number of rejected hypothesis
    n_rejected = len(res)

    print(rejected)
    
    n_rjected = 0
    
    #Update list of remaining strategies
    [strats_ix.remove(x) for x in rejected]
    
 
