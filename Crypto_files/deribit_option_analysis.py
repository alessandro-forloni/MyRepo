# -*- coding: utf-8 -*-
"""
Created on Mon Feb  4 13:08:51 2019

@author: alforlon
"""

from __future__ import division

import requests as req
import numpy as np
from math import sqrt, exp, log
from scipy.stats import norm


def n_d_1(S, K, r, T, sigma):
    

    core = (log(S/K) + (r+sigma**2/2)*T)/(sigma*sqrt(T))
    
    return norm.cdf(core)


def n_d_2(S, K, r, T, sigma):
    

    core = (log(S/K) + (r-sigma**2/2)*T)/(sigma*sqrt(T))
    
    return norm.cdf(core)


def price(S, K, r, T, sigma):
    
    '''
    
    prezzo riespresso in BTC come su piattaforma
    
    '''
    
    return n_d_1(S, K, r, T, sigma) - K/S*exp(-r*T)*n_d_2(S, K, r, T, sigma)




S = 3411
K = 3500
sigma = 0.56
r = 0.1
T = 18/365

#b = 1/np.dot(np.transpose(x), x)*np.dot(x, y)


#%%
#pend = [0]*(len(x)-1)
#
#for i in range(len(x)-1):
#    
#    pend[i] = (Y[i+1]-Y[i])/(X[i+1]-X[i])
#    
#    [0.0002970000000004802,
# 0.0002919999999994616,
# 0.00029900000000088764,
# 0.00029299999999966533,
# 0.0002960000000002765,
# 0.00029299999999966533,
# 0.0002970000000004802,
# 0.00029500000000007276]

#X=[2750, 3000, 3250, 3500, 3750, 4000, 4250, 4500, 4750]
#
#Y=[3339.8115,
# 3339.88575,
# 3339.95875,
# 3340.0335,
# 3340.10675,
# 3340.18075,
# 3340.254,
# 3340.32825,
# 3340.402]


print(price(S, K, r, T, sigma))
print(n_d_1(S, K, r, T, sigma))