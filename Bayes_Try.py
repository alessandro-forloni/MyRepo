# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 18:41:45 2018

@author: Alessandro

FIRST TRY WITH PYMC3

"""

#from __future__ import division

#%env MKL_THREADING_LAYER=GNU
import numpy as np
import pymc3 as pm
import matplotlib.pyplot as plt
import mpl_tweak_module
import pandas as pd


mpl_tweak_module.set_params()

#%%

n = 100
h = 61
alpha = 2
beta = 2

niter = 1000



with pm.Model() as model: # context management
    # define priors
    p = pm.Beta('p', alpha=alpha, beta=beta)

    # define likelihood
    y = pm.Binomial('y', n=n, p=p, observed=h)

    # inference
    start = pm.find_MAP() # Use MAP estimate (optimization) as the initial state for MCMC
    step = pm.Metropolis() # Have a choice of samplers
    
    trace = pm.sample(niter, step, start)#, random_seed=123, progressbar=False)
    
print('Done')


def model_work(obs):
    
    model = pm.Model()
    
    with model:

        mu = pm.Uniform('mu', lower=-0.01, upper=0.01, shape=(1,))
        sigma = pm.Uniform('sigma', lower=0, upper=0.05, shape=(1,))
    
        y_obs = pm.Normal('Y_obs', mu=mu, sd=sigma, observed=obs)
        
        res = pm.find_MAP()
        
        step = pm.Slice()
    
        #step = pm-Metropolis()
        
        trace = pm.sample(1000, step, res, random_seed=123, progressbar=True)
        
        pm.traceplot(trace, [mu, sigma]);
        
    del model
    
    return res['mu'][0], res['sigma'][0]


fName = 'Analysis_all_strategies_2018-02-11_report_2018-02-11_05_15.xlsx'     

df = pd.read_excel(fName, sheet_name = 'PnLDailyEqualRisk', skiprows = 2)


# generate observed data
#N = 100
#
##Real params
#mu_1 = np.array([0.03])
#mu_21 = np.array([0.05])
#mu_22 = np.array([-0.05])
#
#
#sigma_1 = np.array([0.1])
#sigma_21 = np.array([0.04])
#sigma_22 = np.array([0.06])
#
#niter = 1000
#
#y1 = np.random.normal(mu_1, sigma_1, N)
#y21 = np.random.normal(mu_21, sigma_21, int(N/2))
#y22 = np.random.normal(mu_22, sigma_22, int(N/2))
#
#y2 = np.array(list(y21) + list(y22))

df = df.iloc[:,1:]
df.iloc[0,:] = np.ones(df.shape[1])*100000

df_cumulative = df.cumsum()
df_return = df_cumulative/df_cumulative.shift(1) - 1

df_return.dropna(how = 'any', inplace = True)

y1 = df_return.iloc[:,3].values[:500]
y2 = df_return.iloc[:,4].values[:500]

N = len(y1)
#plt.figure()
#plt.plot(np.cumprod(1+y1))
#plt.plot(np.cumprod(1+y2))

#%%
#basic_model_1 = pm.Model()
#basic_model_2 = pm.Model()

mu_est_1 = np.zeros(N)
mu_est_2 = np.zeros(N)

sigma_est_1 = np.zeros(N)
sigma_est_2 = np.zeros(N)


mu_est_1[:10] = y1[:10].mean()
mu_est_2[:10] = y2[:10].mean()

sigma_est_1[:10] = y1[:10].std()
sigma_est_2[:10] = y2[:10].std()

#for i in range(10, N):
#
#        print(i)
#        mu_est_1[i], sigma_est_1[i] = model_work(y1[:i])
#        mu_est_2[i], sigma_est_2[i] = model_work(y2[:i])

mu_est_1, sigma_est_1 = model_work(y1)
mu_est_2, sigma_est_2 = model_work(y2)

#%%
range_up_1 = mu_est_1 + sigma_est_1
range_down_1 = mu_est_1 - sigma_est_1

range_up_2 = mu_est_2 + sigma_est_2
range_down_2 = mu_est_2 - sigma_est_2


fig = plt.figure()
ax1 = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

ax2.fill_between(range(0, N), range_down_1, range_up_1, color = 'blue', alpha = 0.5)
ax2.fill_between(range(0, N), range_down_2, range_up_2, color = 'orange', alpha = 0.5)


ax1.plot(np.cumprod(1+y1))
ax1.plot(np.cumprod(1+y2))

ax2.plot(mu_est_1)
ax2.plot(mu_est_2)     

ax2.plot(np.zeros(N), 'r--')


